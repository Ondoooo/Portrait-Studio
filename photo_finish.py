"""Photographic finishes for floating-point RGB tensors in [0, 1], with channels last."""
import torch


def gentle_contrast(image):
    """Apply a small luminance S-curve with explicit per-pixel highlight headroom."""
    weights = image.new_tensor([.2126, .7152, .0722])
    luma = (image*weights).sum(dim=-1, keepdim=True)
    offset = .18*luma*(1-luma)*(2*luma-1)
    offset = torch.minimum(torch.maximum(offset, -image.amin(dim=-1, keepdim=True)),
                           1-image.amax(dim=-1, keepdim=True))
    return image+offset


def fine_detail(image):
    """A bounded luminance-only unsharp mask at the final display resolution."""
    luma = (image * image.new_tensor([.2126, .7152, .0722])).sum(dim=-1, keepdim=True)
    padded = torch.nn.functional.pad(luma.movedim(-1, 1), (1, 1, 1, 1), mode="replicate")
    blurred = torch.nn.functional.avg_pool2d(padded, kernel_size=3, stride=1).movedim(1, -1)
    detail = luma - blurred
    offset = (.7 * detail.sign() * (detail.abs() - 1 / 255).clamp_min(0)).clamp(-6 / 255, 6 / 255)
    offset = torch.minimum(torch.maximum(offset, -image.amin(dim=-1, keepdim=True)),
                           1 - image.amax(dim=-1, keepdim=True))
    return image + offset
