import numpy as np
import pytest
from delaynet import connectivity


@pytest.mark.parametrize(
    "approach,mi_kwargs",
    [
        ("ordinal", {"embedding_dim": 3}),
        ("bayes", {"alpha": "jeffrey"}),
        ("grassberger", {}),
        ("metric", {}),
        ("tsallis", {"q": 0.9}),
        ("discrete", {}),
    ],
)
def test_mutual_information(approach, mi_kwargs):
    # Generate some test time series data
    np.random.seed(24567)
    ts1 = np.random.normal(0, 1, size=100)
    ts2 = np.roll(ts1, 2) + np.random.normal(
        0, 0.1, size=100
    )  # Create causally related series

    # Test the connectivity with specified parameters
    result = connectivity(
        ts1,
        ts2,
        metric="mutual_information",
        approach=approach,
        lag_steps=2,
        **mi_kwargs,
    )

    # Assert that the function returns expected format
    assert isinstance(result, tuple), "Result should be a tuple"
    assert len(result) == 2, "Result should contain two elements"


def test_mutual_information_missing_approach():
    """Test mutual information with missing approach."""
    with pytest.raises(ValueError, match="The approach parameter must be given."):
        connectivity(
            np.ones(40),
            np.ones(40),
            metric="mutual_information",
            lag_steps=2,
        )
