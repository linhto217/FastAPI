# Banking Transactions API

A high-performance REST API built with FastAPI for analyzing banking transaction data with real-time fraud detection capabilities. Designed for production workloads with optimized data loading, precomputed statistics, and a clean service-oriented architecture.

## Features

- **20 REST Endpoints** across 5 categories: Transactions, Statistics, Fraud, Customers, System
- **Rule-Based Fraud Detection** with configurable heuristics and probability scoring
- **Optimized Data Loading** using pandas with memory-efficient dtypes
- **Precomputed Statistics** at startup for instant response times
- **Abstract Data Access Layer** for easy database migration
- **Comprehensive Test Suite** with 85%+ coverage enforcement
- **Interactive API Documentation** via Swagger UI and ReDoc

## Prerequisites

- Python 3.12+
- pip or conda for package management

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/banking-transactions-api.git
cd banking-transactions-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

### Install as Package

```bash
pip install -e .
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_MODE` | Enable test mode (allows DELETE, uses test data) | `0` |
| `DATA_PATH` | Path to production CSV file | `data/transactions_data.csv` |
| `TEST_DATA_PATH` | Path to test CSV file | `data/test_transactions_data.csv` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

## Running the API

```bash
# Development server with auto-reload
uvicorn banking_api.main:app --reload

# Production server
uvicorn banking_api.main:app --host 0.0.0.0 --port 8000

# Test mode (enables DELETE endpoint)
TEST_MODE=1 uvicorn banking_api.main:app --reload
```

Access the API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Transactions (Routes 1-8)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/transactions` | Paginated list with filters (type, isFraud, amount range) |
| `GET` | `/api/transactions/{id}` | Get transaction by ID |
| `POST` | `/api/transactions/search` | Advanced search with multiple criteria |
| `GET` | `/api/transactions/types` | List available transaction types |
| `GET` | `/api/transactions/recent` | Get N most recent transactions |
| `GET` | `/api/transactions/from/{customer_id}` | Transactions sent by customer |
| `GET` | `/api/transactions/to/{customer_id}` | Transactions received by customer |
| `DELETE` | `/api/transactions/{id}` | Delete transaction (test mode only) |

### Statistics (Routes 9-12)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/stats/overview` | Global statistics (total, amounts, fraud rate) |
| `GET` | `/api/stats/by-type` | Statistics grouped by transaction type |
| `GET` | `/api/stats/amount-distribution` | Amount histogram with configurable bins |
| `GET` | `/api/stats/daily` | Aggregated daily statistics |

### Fraud Detection (Routes 13-15)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/fraud/summary` | Fraud overview with precision/recall |
| `GET` | `/api/fraud/by-type` | Fraud breakdown by transaction type |
| `POST` | `/api/fraud/predict` | Predict fraud probability for a transaction |

### Customers (Routes 16-18)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/customers` | Paginated customer list |
| `GET` | `/api/customers/{id}` | Customer profile with transaction stats |
| `GET` | `/api/customers/top/{n}` | Top N customers by transaction volume |

### System (Routes 19-20)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/system/health` | Health check with uptime and status |
| `GET` | `/api/system/metadata` | Service version and dataset info |

## Fraud Detection

The API uses a rule-based scoring system to detect potentially fraudulent transactions:

| Rule | Score | Condition |
|------|-------|-----------|
| Balance Inconsistency | +0.3 | Expected balance ≠ actual balance |
| Risky Transaction Type | +0.3 | Type is `CASH_OUT` or `TRANSFER` |
| High Amount | +0.4 | Amount > 100,000 |
| Rapid Transactions | +0.3 | Multiple transactions within 1 hour |

**Fraud Threshold**: Total score > 0.5 → flagged as fraud

### Example Prediction Request

```bash
curl -X POST "http://localhost:8000/api/fraud/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TRANSFER",
    "amount": 150000,
    "oldbalanceOrg": 200000,
    "newbalanceOrig": 50000,
    "nameOrig": "C1234567890"
  }'
```

## Data Format

The API expects CSV files with the following schema (PaySim format):

| Column | Type | Description |
|--------|------|-------------|
| `step` | int | Time unit (1 step = 1 hour) |
| `type` | string | PAYMENT, TRANSFER, CASH_OUT, CASH_IN, DEBIT |
| `amount` | float | Transaction amount |
| `nameOrig` | string | Origin customer ID |
| `oldbalanceOrg` | float | Origin balance before |
| `newbalanceOrig` | float | Origin balance after |
| `nameDest` | string | Destination customer/merchant ID |
| `oldbalanceDest` | float | Destination balance before |
| `newbalanceDest` | float | Destination balance after |
| `isFraud` | int | Fraud label (0 or 1) |
| `isFlaggedFraud` | int | Flagged by legacy system (0 or 1) |

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=banking_api --cov-report=term-missing

# Run specific test file
pytest tests/test_transactions.py -v

# Run with verbose output
pytest -v --tb=short
```

**Coverage Requirement**: Tests must maintain ≥85% code coverage.

## Project Structure

```
banking-transactions-api/
├── banking_api/
│   ├── __init__.py              # Package version
│   ├── main.py                  # FastAPI app with lifespan
│   ├── exceptions.py            # Custom exception classes
│   ├── data/
│   │   ├── base.py              # Abstract DataAccessLayer
│   │   ├── dataframe_dal.py     # Pandas implementation
│   │   └── loader.py            # CSV validation & loading
│   ├── models/
│   │   ├── transaction.py       # Transaction schemas
│   │   ├── customer.py          # Customer schemas
│   │   ├── fraud.py             # Fraud prediction schemas
│   │   ├── stats.py             # Statistics schemas
│   │   └── responses.py         # API response wrappers
│   ├── services/
│   │   ├── transactions_service.py
│   │   ├── stats_service.py
│   │   ├── fraud_detection_service.py
│   │   ├── customer_service.py
│   │   └── system_service.py
│   └── routers/
│       ├── transactions.py      # Routes 1-8
│       ├── stats.py             # Routes 9-12
│       ├── fraud.py             # Routes 13-15
│       ├── customers.py         # Routes 16-18
│       └── system.py            # Routes 19-20
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_transactions.py
│   ├── test_stats.py
│   ├── test_fraud.py
│   ├── test_customers.py
│   ├── test_system.py
│   └── test_services/
│       ├── test_fraud_detection.py
│       └── test_data_layer.py
├── data/
│   └── test_transactions_data.csv
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── setup.py                     # Package configuration
├── pyproject.toml               # Build system config
├── pytest.ini                   # Test configuration
└── .env.example                 # Environment template
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Routers   │────▶│   Services   │────▶│ DataAccessLayer │
│  (FastAPI)  │     │   (Logic)    │     │   (Abstract)    │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                           ┌──────────────────────┼──────────────────────┐
                           │                      │                      │
                    ┌──────▼──────┐        ┌──────▼──────┐        ┌──────▼──────┐
                    │ DataFrameDAL│        │  Future DB  │        │  Future DB  │
                    │  (Pandas)   │        │  (Postgres) │        │   (Mongo)   │
                    └─────────────┘        └─────────────┘        └─────────────┘
```

## Development

### Code Quality

```bash
# Linting
flake8 banking_api tests --max-line-length=100

# Type checking
mypy banking_api --ignore-missing-imports
```

### Adding New Endpoints

1. Define Pydantic models in `banking_api/models/`
2. Implement business logic in `banking_api/services/`
3. Create route handler in `banking_api/routers/`
4. Register router in `banking_api/main.py`
5. Add tests in `tests/`

## Dependencies

### Production
- **FastAPI** ≥0.109.0 - Web framework
- **Uvicorn** ≥0.27.0 - ASGI server
- **Pydantic** ≥2.5.0 - Data validation
- **Pandas** ≥2.1.0 - Data processing
- **python-dotenv** ≥1.0.0 - Environment management

### Development
- **pytest** ≥7.4.0 - Testing framework
- **pytest-cov** ≥4.1.0 - Coverage reporting
- **pytest-asyncio** ≥0.21.0 - Async test support
- **httpx** ≥0.25.0 - HTTP client for testing
- **flake8** ≥6.1.0 - Linting
- **mypy** ≥1.7.0 - Type checking

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Version**: 1.0.0 | **Python**: 3.12+ | **Framework**: FastAPI
