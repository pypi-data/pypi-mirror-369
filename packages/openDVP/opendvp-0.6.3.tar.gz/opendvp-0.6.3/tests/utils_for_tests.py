import numpy as np
import pandas as pd
from anndata import AnnData


def small_anndata():
    # Create fake data: 30 samples, 3 proteins
    np.random.seed(42)
    n_samples = 30
    n_proteins = 3

    # Simulate protein abundance data
    X = np.random.normal(loc=10, scale=2, size=(n_samples, n_proteins))

    # Create categorical groupings
    groups = np.random.choice(["A", "B", "C"], size=n_samples)
    batches = np.random.choice(["Batch1", "Batch2"], size=n_samples)

    # Create AnnData object
    adata = AnnData(
        X=X,
        obs=pd.DataFrame({"group": groups, "batch": batches}),
        var=pd.DataFrame(index=[f"Protein{i + 1}" for i in range(n_proteins)]),
    )

    return adata
