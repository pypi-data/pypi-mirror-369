"""Functions for interoperability between cupy and pytorch."""

from torch import Tensor

from warnings import warn
import torch
import numpy as np

try:
    import cupy as cp

    cupy_enabled = True
except ImportError:
    import numpy as cp

    cupy_enabled = False


__all__ = ["to_pytorch", "from_pytorch", "get_device"]


def get_device(arr) -> torch.device:
    """Bootleg version of sigpy's more-robust get_device"""
    if isinstance(arr, np.ndarray):
        return torch.device("cpu")
    elif cupy_enabled and isinstance(arr, cp.ndarray):
        return torch.device(f"cuda:{arr.device.id}")
    elif isinstance(arr, Tensor):
        return arr.device
    else:
        raise ValueError(f"Can't get device of array type: {type(arr)}")


def to_pytorch(array, requires_grad: bool = False):
    """Zero-copy conversion from numpy/cupy array to pytorch tensor.

    For complex array input, returns a tensor with shape + [2],
    where tensor[..., 0] and tensor[..., 1] represent the real
    and imaginary.

    Args:
        array (numpy/cupy array): input.
        requires_grad(bool): Set .requires_grad output tensor
    Returns:
        PyTorch tensor.

    """
    return torch.as_tensor(array).requires_grad_(requires_grad)

    # import torch
    # from torch.utils.dlpack import from_dlpack

    # device = get_device(array)

    # if device.type == "cpu":
    #     tensor = torch.from_numpy(array)
    # else:
    #     tensor = from_dlpack(array.toDlpack())

    # tensor.requires_grad = requires_grad
    # return tensor.contiguous()


def from_pytorch(tensor):  # pragma: no cover
    """Zero-copy conversion from pytorch tensor to numpy/cupy array.

    If iscomplex, then tensor must have the last dimension as 2,
    and the output will be viewed as a complex valued array.

    Args:
        tensor (PyTorch tensor): input.
        iscomplex (bool): whether input represents complex valued tensor.

    Returns:
        Numpy/cupy array.

    """
    device = tensor.device
    if device.type == "cpu":
        output = tensor.detach().contiguous().numpy()
    else:
        if cupy_enabled:
            output = cp.asarray(tensor)
        else:
            raise TypeError(
                "CuPy not installed, but trying to convert GPU PyTorch Tensor."
            )
    return output
