import pytest

from math import prod

import torch
import sigpy as sp

from torchlinops.functional import fold
from torchlinops.functional._unfold.nblocks import get_nblocks
from torchlinops.utils import from_pytorch, to_pytorch


PYTEST_GPU_MARKS = [
    pytest.mark.gpu,
    pytest.mark.skipif(
        not torch.cuda.is_available(), reason="GPU is required but not available"
    ),
]


@pytest.mark.parametrize("dev", ["cpu", pytest.param("cuda", marks=PYTEST_GPU_MARKS)])
@pytest.mark.parametrize("dtype", ["float32", "float64", "complex64"])
@pytest.mark.parametrize(
    "spec",
    [
        "small1d",
        "medium1d",
        pytest.param("large1d", marks=PYTEST_GPU_MARKS),
        "tiny2d",
        "small2d",
        "medium2d",
        pytest.param("large2d", marks=PYTEST_GPU_MARKS),
        pytest.param("small3d", marks=PYTEST_GPU_MARKS),
        pytest.param("medium3d", marks=PYTEST_GPU_MARKS),
        pytest.param("large3d", marks=PYTEST_GPU_MARKS + [pytest.mark.slow]),
        pytest.param("verylarge3d", marks=PYTEST_GPU_MARKS + [pytest.mark.slow]),
    ],
)
def test_fold(dev, dtype, spec, request):
    spec = request.getfixturevalue(spec)
    device = torch.device(dev)
    if dtype == "float32":
        dtype = torch.float32
    elif dtype == "float64":
        dtype = torch.float64
    elif dtype == "complex64":
        dtype = torch.complex64

    spec["nblocks"] = get_nblocks(spec["shape"], spec["block_size"], spec["stride"])

    ishape = (*spec["N"], *spec["nblocks"], *spec["block_size"])
    oshape = (*spec["N"], *spec["shape"])

    x = torch.arange(prod(ishape)).reshape(ishape)
    # x = torch.ones(prod(ishape)).reshape(ishape)

    x = x.to(device).to(dtype)

    y_th = fold(x, spec["shape"], spec["block_size"], spec["stride"])

    x = from_pytorch(x)
    y_sp = sp.blocks_to_array(x, oshape, spec["block_size"], spec["stride"])
    assert torch.allclose(y_th, to_pytorch(y_sp))
