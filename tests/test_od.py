import numpy as np
import pandas as pd
import pytest

from cryptodatapy.transform.od import OutlierDetection

# get data for testing
@pytest.fixture
def raw_oc_data():
    return pd.read_csv('data/cc_raw_oc_df.csv', index_col=[0, 1], parse_dates=['date'])

@pytest.fixture
def raw_ohlcv_data():
    return pd.read_csv('data/cc_raw_ohlcv_df.csv', index_col=[0, 1], parse_dates=['date'])


def test_od_atr(raw_ohlcv_data) -> None:
    """
    Test outlier detection ATR method.
    """
    # outlier detection
    df = OutlierDetection(raw_ohlcv_data).atr()
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_ohlcv_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.loc[:, :"close"].notna().sum()
        / raw_ohlcv_data.loc[:, :"close"].notna().sum()
        < 0.05
    ), "Some series have more than 5% of values filtered as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_iqr(raw_oc_data) -> None:
    """
    Test outlier detection IQR method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).iqr()
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.05
    ), "Some series have more than 5% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_mad(raw_oc_data) -> None:
    """
    Test outlier detection MAD method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).mad()
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.2
    ), "Some series have more than 20% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_zscore(raw_oc_data) -> None:
    """
    Test outlier detection z-score method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).z_score(thresh_val=2)
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.05
    ), "Some series have more than 5% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_ewma(raw_oc_data) -> None:
    """
    Test outlier detection exponential weighted moving average method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).ewma(thresh_val=1.5)
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.05
    ), "Some series have more than 5% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_seasonal_decomp(raw_oc_data) -> None:
    """
    Test outlier detection seasonal decomposition method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).seasonal_decomp(thresh_val=10)
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.2
    ), "Some series have more than 20% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_stl(raw_oc_data) -> None:
    """
    Test outlier detection seasonal decomposition method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).stl(thresh_val=10)
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.25
    ), "Some series have more than 25% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


def test_od_prophet(raw_oc_data) -> None:
    """
    Test outlier detection prophet method.
    """
    # outlier detection
    df = OutlierDetection(raw_oc_data).prophet()
    outliers_df = df["outliers"]
    # assert statements
    assert (
        outliers_df.shape == raw_oc_data.shape
    ), "Outliers dataframe changed shape."  # shape
    assert isinstance(
        outliers_df.index, pd.MultiIndex
    ), "Dataframe should be multiIndex."  # multiindex
    assert isinstance(
        outliers_df.index.droplevel(1), pd.DatetimeIndex
    ), "Index is not DatetimeIndex."  # datetimeindex
    assert all(
        outliers_df.notna().sum() / raw_oc_data.notna().sum() < 0.1
    ), "Some series have more than 10% of values detected as outliers in dataframe."  # % outliers
    assert not any(
        (outliers_df.describe().loc["max"] == np.inf)
        & (outliers_df.describe().loc["min"] == -np.inf)
    ), "Inf values found in the dataframe"  # inf


if __name__ == "__main__":
    pytest.main()
