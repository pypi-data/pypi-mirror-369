__all__ = [
    "masked_cross_entropy",
    "adaptive_l1_loss",
    "contrastive_loss",
    "smooth_l1_loss",
    "hybrid_loss",
    "diff_loss",
    "cosine_loss",
    "ft_n_loss",
    "MultiMelScaleLoss",
    "MelLoss",
    "multi_mel_scale_loss_cfg",
    "TrainTracker",
]
import copy
import torch
import torchaudio
from torch import nn, Tensor
from lt_utils.common import *
import torch.nn.functional as F
from lt_tensor.model_base import Model
from lt_utils.misc_utils import get_current_time
from lt_utils.file_ops import load_json, save_json
from lt_tensor.misc_utils import plot_view


def ft_n_loss(output: Tensor, target: Tensor, weight: Optional[Tensor] = None):
    if weight is not None:
        return torch.mean((torch.abs(output - target) + weight) ** 0.5)
    return torch.mean(torch.abs(output - target) ** 0.5)


def adaptive_l1_loss(
    inp: Tensor,
    tgt: Tensor,
    weight: Optional[Tensor] = None,
    scale: float = 1.0,
    inverted: bool = False,
):

    if weight is not None:
        loss = torch.mean(torch.abs((inp - tgt) + weight.mean()))
    else:
        loss = torch.mean(torch.abs(inp - tgt))
    loss *= scale
    if inverted:
        return -loss
    return loss


def smooth_l1_loss(inp: Tensor, tgt: Tensor, beta=1.0, weight=None):
    diff = torch.abs(inp - tgt)
    loss = torch.where(diff < beta, 0.5 * diff**2 / beta, diff - 0.5 * beta)
    if weight is not None:
        loss *= weight
    return loss.mean()


def contrastive_loss(x1: Tensor, x2: Tensor, label: Tensor, margin: float = 1.0):
    # label == 1: similar, label == 0: dissimilar
    dist = torch.nn.functional.pairwise_distance(x1, x2)
    loss = label * dist**2 + (1 - label) * torch.clamp(margin - dist, min=0.0) ** 2
    return loss.mean()


def cosine_loss(inp, tgt):
    cos = torch.nn.functional.cosine_similarity(inp, tgt, dim=-1)
    return 1 - cos.mean()  # Lower is better


def masked_cross_entropy(
    logits: torch.Tensor,  # [B, T, V]
    targets: torch.Tensor,  # [B, T]
    lengths: torch.Tensor,  # [B]
    reduction: str = "mean",
) -> torch.Tensor:
    """
    CrossEntropyLoss with masking for variable-length sequences.
    - logits: unnormalized scores [B, T, V]
    - targets: ground truth indices [B, T]
    - lengths: actual sequence lengths [B]
    """
    B, T, V = logits.size()
    logits = logits.view(-1, V)
    targets = targets.view(-1)

    # Create mask
    mask = torch.arange(T, device=lengths.device).expand(B, T) < lengths.unsqueeze(1)
    mask = mask.reshape(-1)

    # Apply CE only where mask == True
    loss = F.cross_entropy(
        logits[mask], targets[mask], reduction="mean" if reduction == "mean" else "none"
    )
    if reduction == "none":
        return loss
    return loss


def diff_loss(pred_noise, true_noise, mask=None):
    """Standard diffusion noise-prediction loss (e.g., DDPM)"""
    if mask is not None:
        return F.mse_loss(pred_noise * mask, true_noise * mask)
    return F.mse_loss(pred_noise, true_noise)


def hybrid_diff_loss(pred_noise, true_noise, alpha=0.5):
    """Combines L1 and L2"""
    l1 = F.l1_loss(pred_noise, true_noise)
    l2 = F.mse_loss(pred_noise, true_noise)
    return alpha * l1 + (1 - alpha) * l2


def gan_d_loss(real_preds, fake_preds, use_lsgan=True):
    loss = 0
    for real, fake in zip(real_preds, fake_preds):
        if use_lsgan:
            loss += F.mse_loss(real, torch.ones_like(real)) + F.mse_loss(
                fake, torch.zeros_like(fake)
            )
        else:
            loss += -torch.mean(torch.log(real + 1e-7)) - torch.mean(
                torch.log(1 - fake + 1e-7)
            )
    return loss


def multi_mel_scale_loss_cfg(option: int = 0):
    match option:
        case 0:
            dict(
                n_mels=[20, 40, 80, 160],
                window_lengths=[256, 512, 1024, 2048],
                n_ffts=[256, 512, 1024, 2048],
                hops=[64, 128, 256, 512],
                f_min=[0, 0, 0, 0],
                f_max=[None, None, None, None],
            )
        case 1:
            dict(
                n_mels=[96, 128, 256],
                window_lengths=[512, 1024, 2048],
                n_ffts=[512, 1024, 2048],
                hops=[128, 256, 512],
                f_min=[0, 0, 0],
                f_max=[None, None, None],
            )
        case _:
            return dict(
                n_mels=[5, 10, 20, 40, 80, 160, 320],
                window_lengths=[32, 64, 128, 256, 512, 1024, 2048],
                n_ffts=[32, 64, 128, 256, 512, 1024, 2048],
                hops=[8, 16, 32, 64, 128, 256, 512],
                f_min=[0, 0, 0, 0, 0, 0, 0],
                f_max=[None, None, None, None, None, None, None],
            )


class MelLoss(Model):
    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        window_length: int = 1024,
        n_fft: int = 1024,
        hop_length: int = 256,
        f_min: float = 0,
        f_max: Optional[float] = None,
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        weight: float = 1.0,
    ):
        super().__init__()
        self.mel_fn = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            center=center,
            onesided=onesided,
            normalized=normalized,
            power=power,
            pad_mode=pad_mode,
            n_fft=n_fft,
            hop_length=hop_length,
            win_length=window_length,
            n_mels=n_mels,
            f_min=f_min,
            f_max=f_max,
        )
        self.loss_fn = loss_fn
        self.weight = weight

    def forward(self, wave: Tensor, target: Tensor):
        x_mels = self.mel_fn.forward(wave)
        y_mels = self.mel_fn.forward(target)
        return self.loss_fn(x_mels, y_mels) * self.weight

    def _forward(
        self,
        inp: Tensor,
        out: Tensor,
        previous_loss: Optional[Tensor] = None,
    ):
        if previous_loss is None:
            return self.forward(inp, out)
        previous_loss += self.forward(inp, out)
        return previous_loss


class MultiMelScaleLoss(Model):
    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: List[int] = [20, 40, 80, 160],
        window_lengths: List[int] = [256, 512, 1024, 2048],
        n_ffts: List[int] = [256, 512, 1024, 2048],
        hops: List[int] = [64, 128, 256, 512],
        f_min: List[float] = [0, 0, 0, 0],
        f_max: List[Optional[float]] = [None, None, None, None],
        loss_fn: Callable[[Tensor, Tensor], Tensor] = nn.L1Loss(),
        center: bool = False,
        power: float = 1.0,
        normalized: bool = False,
        pad_mode: str = "reflect",
        onesided: Optional[bool] = None,
        weight: float = 1.0,
    ):
        super().__init__()
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        self._setup_mels(
            sample_rate,
            n_mels,
            window_lengths,
            n_ffts,
            hops,
            f_min,
            f_max,
            center,
            power,
            normalized,
            pad_mode,
            onesided,
            loss_fn,
            weight,
        )

    def _setup_mels(
        self,
        sample_rate: int,
        n_mels: List[int],
        window_lengths: List[int],
        n_ffts: List[int],
        hops: List[int],
        f_min: List[float],
        f_max: List[Optional[float]],
        center: bool,
        power: float,
        normalized: bool,
        pad_mode: str,
        onesided: Optional[bool],
        loss_fn: Callable,
        weight: float,
    ):
        assert (
            len(n_mels)
            == len(window_lengths)
            == len(n_ffts)
            == len(hops)
            == len(f_min)
            == len(f_max)
        )
        _mel_kwargs = dict(
            sample_rate=sample_rate,
            center=center,
            onesided=onesided,
            normalized=normalized,
            power=power,
            pad_mode=pad_mode,
            loss_fn=loss_fn,
            weight=weight,
        )

        self.mel_losses: List[MelLoss] = nn.ModuleList(
            [
                MelLoss(
                    **_mel_kwargs,
                    n_fft=n_fft,
                    hop_length=hop,
                    window_length=win,
                    n_mels=mel,
                    f_min=fmin,
                    f_max=fmax,
                )
                for mel, win, n_fft, hop, fmin, fmax in zip(
                    n_mels, window_lengths, n_ffts, hops, f_min, f_max
                )
            ]
        )

    def forward(
        self, input_wave: torch.Tensor, target_wave: torch.Tensor
    ) -> torch.Tensor:
        loss = None
        for loss_fn in self.mel_losses:
            loss = loss_fn._forward(input_wave, target_wave)
        return loss


class TrainTracker:
    last_file = f"logs/history_{get_current_time()}.json"
    loss_history: Dict[str, List[Number]] = {}
    lr_history: Dict[str, List[Number]] = {}

    def __init__(self, max_len: int = 100_000, max_len_percent_removal: float = 0.1):
        self.set_max_history(max_len, max_len_percent_removal)

    def set_max_history(
        self, max_len: int = 100_000, max_len_percent_removal: float = 0.1
    ):
        self.max_len = max(int(max_len), 10)
        self.percentage_removal = min(max(float(max_len_percent_removal), 0.1), 0.95)
        self.removal_length = max(int(self.max_len * self.percentage_removal), 4)

    def add_lr(
        self,
        lr: Union[float, Tensor],
        key: str = "main",
    ):
        if key not in self.lr_history:
            self.lr_history[key] = []

        if isinstance(lr, Tensor):
            lr = lr.item()

        self.lr_history[key].append(lr)
        if len(self.lr_history[key]) > self.max_len:
            nc = copy.deepcopy(self.lr_history[key][self.removal_length :])
            self.lr_history[key].clear()
            self.lr_history[key] = nc.copy()

    def add_loss(
        self,
        loss: Union[float, Tensor],
        key: str = "main",
    ):
        if key not in self.loss_history:
            self.loss_history[key] = []
        if isinstance(loss, Tensor):
            loss = loss.item()
        self.loss_history[key].append(float(loss))
        if len(self.loss_history[key]) > self.max_len:
            nc = copy.deepcopy(self.loss_history[key][self.removal_length :])
            self.loss_history[key].clear()
            self.loss_history[key] = nc.copy()

    @staticmethod
    def _sum_and_avg(values: List[Number]):
        if not values:
            return float("nan")
        return sum(values) / len(values)

    def get_lr_average(self, key: str = "main", total: int = 0):
        lr = self.get_learning_rates(key, total)
        return self._sum_and_avg(lr)

    def get_loss_average(self, key: str = "main", total: int = 0):
        losses = self.get_losses(key, total)
        return self._sum_and_avg(losses)

    def get_learning_rates(self, key: str = "train", total: int = 0):
        total = max(int(total), 0)
        results = self.lr_history.get(key, [])
        if total:
            return results[-total:]
        return results

    def get_losses(self, key: str = "main", total: int = 0):
        total = max(int(total), 0)
        results = self.loss_history.get(key, [])
        if total:
            return results[-total:]
        return results

    def save(self, path: Optional[PathLike] = None):
        if path is None:
            path = f"logs/history_{get_current_time()}.json"
        save_json(path, self.loss_history, indent=2)
        self.last_file = str(path)

    def load(self, path: Optional[PathLike] = None):
        if path is None:
            path = self.last_file
        self.loss_history = load_json(path, {})
        self.last_file = str(path)

    def plot_loss(
        self,
        keys: Union[str, List[str]] = ["main"],
        max_amount: int = 0,
        smoothing: bool = False,
        smoothing_alpha: float = 0.5,
        title: str = "Loss(es)",
    ):
        if isinstance(keys, str):
            keys = [keys]
        max_amount = min(self.max_len, max(int(max_amount), 0))
        if not max_amount:
            max_amount = self.max_len
        return plot_view(
            {k: v[-max_amount:] for k, v in self.loss_history.items() if k in keys},
            title,
            smoothing=smoothing,
            smoothing_alpha=smoothing_alpha,
        )

    def plot_lr(
        self,
        keys: Union[str, List[str]] = ["main"],
        max_amount: int = 0,
        smoothing: bool = False,
        smoothing_alpha: float = 0.5,
        title: str = "Learning Rate(s)",
    ):
        if isinstance(keys, str):
            keys = [keys]
        max_amount = min(self.max_len, max(int(max_amount), 0))
        if not max_amount:
            max_amount = self.max_len
        return plot_view(
            {k: v[-max_amount:] for k, v in self.lr_history.items() if k in keys},
            title,
            smoothing=smoothing,
            smoothing_alpha=smoothing_alpha,
        )
