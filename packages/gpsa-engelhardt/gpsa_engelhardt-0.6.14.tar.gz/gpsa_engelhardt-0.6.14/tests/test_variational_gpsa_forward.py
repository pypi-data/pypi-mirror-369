# tests/test_variational_gpsa_forward.py

import warnings
warnings.filterwarnings(
    "ignore",
    message="torch.cholesky is deprecated in favor of torch.linalg.cholesky",
)

import numpy as np
import torch
from gpsa import VariationalGPSA
from gpsa import rbf_kernel

def test_variational_gpsa_forward_runs_without_error():
    # 1. Create toy one‐view data
    np.random.seed(0)
    X = np.random.rand(50, 2)
    Y = np.sin(2 * np.pi * X[:, 0])[:, None] + 0.1 * np.random.randn(50, 1)

    x = torch.tensor(X, dtype=torch.float32)
    y = torch.tensor(Y, dtype=torch.float32)
    view_idx       = [np.arange(X.shape[0])]
    n_samples_list = [X.shape[0]]

    data_dict = {
        "demo": {
            "spatial_coords": x,
            "outputs":        y,
            "n_samples_list": n_samples_list,
        }
    }

    # 2. Instantiate the variational model
    model = VariationalGPSA(
        data_dict,
        n_spatial_dims=2,
        m_G=10,
        m_X_per_view=10,
        data_init=True,
        minmax_init=False,
        grid_init=False,
        n_latent_gps={"demo": None},
        mean_function="identity_fixed",
        kernel_func_warp=rbf_kernel,
        kernel_func_data=rbf_kernel,
        fixed_view_idx=0,
    ).to("cpu")

    # 3. One forward pass
    view_dict, Ns, _, _ = model.create_view_idx_dict(data_dict)
    G_means, G_samples, F_latent_samples, F_samples = model.forward(
        {"demo": x},
        view_idx=view_dict,
        Ns=Ns,
        S=5,
    )

    # 4. Basic assertions to ensure shapes look right
    assert "demo" in G_means
    assert G_means["demo"].ndim == 2

    # F_samples is a dict, so ensure it has the expected structure
    assert isinstance(F_samples, dict)
    assert "demo" in F_samples
    demo_tensor = F_samples["demo"]
    assert isinstance(demo_tensor, torch.Tensor)
    assert demo_tensor.ndim >= 2
