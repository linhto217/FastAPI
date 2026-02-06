"""Test configuration and fixtures.

This module provides pytest fixtures for testing the Banking Transactions API.
"""
import os
import sys
from datetime import datetime
from typing import Generator

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Set test mode before importing app
os.environ["TEST_MODE"] = "1"
os.environ["TEST_DATA_PATH"] = "data/test_transactions_data.csv"

from banking_api.data.dataframe_dal import DataFrameDAL
from banking_api.main import app
from banking_api.services.fraud_detection_service import compute_fraud_stats
from banking_api.services.stats_service import compute_all_stats


@pytest.fixture(scope="session")
def sample_dataframe() -> pd.DataFrame:
    """Create a sample DataFrame for testing.

    Returns
    -------
    pd.DataFrame
        Sample transaction data.
    """
    data = {
        "id": [f"tx_{i:07d}" for i in range(10)],
        "step": [1, 1, 1, 2, 2, 3, 3, 4, 5, 5],
        "type": ["PAYMENT", "TRANSFER", "CASH_OUT", "PAYMENT", "TRANSFER",
                 "CASH_IN", "DEBIT", "PAYMENT", "TRANSFER", "CASH_OUT"],
        "amount": [1000.0, 5000.0, 3000.0, 500.0, 150000.0,
                   2000.0, 800.0, 1200.0, 250000.0, 50000.0],
        "nameOrig": ["C001", "C002", "C003", "C001", "C002",
                     "C003", "C001", "C002", "C004", "C004"],
        "oldbalanceOrg": [5000.0, 10000.0, 3000.0, 4000.0, 5000.0,
                         1000.0, 3200.0, 8800.0, 500000.0, 250000.0],
        "newbalanceOrig": [4000.0, 5000.0, 0.0, 3500.0, 0.0,
                          3000.0, 2400.0, 7600.0, 250000.0, 200000.0],
        "nameDest": ["M001", "C004", "C005", "M002", "C006",
                     "C001", "C007", "M001", "C008", "C009"],
        "oldbalanceDest": [0.0, 0.0, 10000.0, 0.0, 0.0,
                          5000.0, 0.0, 0.0, 0.0, 50000.0],
        "newbalanceDest": [0.0, 5000.0, 13000.0, 0.0, 150000.0,
                          3000.0, 800.0, 0.0, 250000.0, 100000.0],
        "isFraud": [0, 1, 1, 0, 1, 0, 0, 0, 1, 0],
        "isFlaggedFraud": [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    }

    df = pd.DataFrame(data)
    df["type"] = df["type"].astype("category")
    df["isFraud"] = df["isFraud"].astype("int8")
    df["isFlaggedFraud"] = df["isFlaggedFraud"].astype("int8")

    return df


@pytest.fixture(scope="session")
def test_dal(sample_dataframe: pd.DataFrame) -> DataFrameDAL:
    """Create a test DAL instance.

    Parameters
    ----------
    sample_dataframe : pd.DataFrame
        The sample transaction DataFrame.

    Returns
    -------
    DataFrameDAL
        Data access layer instance.
    """
    return DataFrameDAL(sample_dataframe)


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app.

    Yields
    ------
    TestClient
        FastAPI test client.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def mock_app_state(sample_dataframe: pd.DataFrame) -> dict:
    """Create mock app state data.

    Parameters
    ----------
    sample_dataframe : pd.DataFrame
        The sample transaction DataFrame.

    Returns
    -------
    dict
        Mock app state containing DAL and cached stats.
    """
    dal = DataFrameDAL(sample_dataframe)
    stats = compute_all_stats(sample_dataframe)
    fraud_stats = compute_fraud_stats(sample_dataframe)

    return {
        "dal": dal,
        "cached_stats": {**stats, **fraud_stats},
        "start_time": datetime.now(),
        "load_time": datetime.now(),
        "customer_timeline": {}
    }


@pytest.fixture
def valid_transaction() -> dict:
    """Create a valid transaction for testing.

    Returns
    -------
    dict
        Valid transaction data.
    """
    return {
        "id": "tx_0000001",
        "step": 1,
        "type": "TRANSFER",
        "amount": 5000.0,
        "nameOrig": "C1234567890",
        "oldbalanceOrg": 10000.0,
        "newbalanceOrig": 5000.0,
        "nameDest": "C0987654321",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 5000.0,
        "isFraud": 0,
        "isFlaggedFraud": 0
    }


@pytest.fixture
def fraud_prediction_request() -> dict:
    """Create a fraud prediction request for testing.

    Returns
    -------
    dict
        Fraud prediction request data.
    """
    return {
        "type": "TRANSFER",
        "amount": 150000.0,
        "oldbalanceOrg": 200000.0,
        "newbalanceOrig": 50000.0
    }


@pytest.fixture
def search_criteria() -> dict:
    """Create search criteria for testing.

    Returns
    -------
    dict
        Search criteria data.
    """
    return {
        "type": "TRANSFER",
        "isFraud": 1,
        "amount_range": [1000, 100000]
    }
