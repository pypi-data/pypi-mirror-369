import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    """Sample dataframe for testing."""
    return pd.DataFrame(
        {"A": [1, 2, np.nan, 4], "B": ["x", np.nan, "z", "w"], "C": [1.1, 2.2, 3.3, np.nan]}
    )


@pytest.fixture
def empty_df():
    """Empty dataframe for testing."""
    return pd.DataFrame()
