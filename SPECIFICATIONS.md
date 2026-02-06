# Banking Transactions API — Specifications

## Project Information
- **Project**: Banking Transactions API  
- **Version**: 1.0  
- **Deadline**: 28 December 2025  
- **Framework**: FastAPI  
- **Language**: Python 3.12+  
- **Deliverables**:
  - Python package
  - Unit tests
  - GitHub Pull Request

---

## 1. General Objective

Develop a complete REST API to expose and manipulate banking transaction data provided by the production team.

The API must:
- Allow consultation, search, and filtering of transactions
- Provide aggregated and analytical statistics
- Integrate fraud detection and monitoring endpoints
- Be documented (NumPyDoc + Swagger optional)
- Be tested (unit tests and feature tests)
- Be packaged as an installable Python module

---

## 2. Endpoints Organization (20 routes total)

| Category        | Description                                 | Routes |
|-----------------|---------------------------------------------|--------|
| Transactions    | Consultation, filtering, search, deletion   | 1–8    |
| Statistics      | Global and criteria-based aggregations      | 9–12   |
| Fraud           | Analysis and detection                      | 13–15  |
| Customers       | Customer portfolio exploration              | 16–18  |
| Administration  | Metadata and service supervision            | 19–20  |

---

## 3. Routes Detail

### Transactions

1. GET /api/transactions
Description: Paginated list of transactions  
Parameters: `page`, `limit`, `type`, `isFraud`, `min_amount`, `max_amount`  

Response:
```json
{
  "page": 1,
  "transactions": [
    { "id": "tx_0001", "amount": 500.0, "type": "CASH_OUT" }
  ]
}

2. GET /api/transactions/{id}

Description: Get transaction details by ID

3. POST /api/transactions/search

Description: Multi-criteria search (POST with JSON body)

Request example:

{
  "type": "TRANSFER",
  "isFraud": 1,
  "amount_range": [1000, 5000]
}

4. GET /api/transactions/types

Description: List available transaction types (unique values of type)

5. GET /api/transactions/recent

Description: Return the N most recent transactions
Parameter: n (default = 10)

6. DELETE /api/transactions/{id}

Description: Delete a fake transaction (test mode only)

7. GET /api/transactions/by-customer/{customer_id}

Description: List transactions sent by a customer (origin)

8. GET /api/transactions/to-customer/{customer_id}

Description: List transactions received by a customer (destination)

Statistics
9. GET /api/stats/overview

Description: Global dataset statistics

Response:

{
  "total_transactions": 6362620,
  "fraud_rate": 0.00129,
  "avg_amount": 178642.15,
  "most_common_type": "CASH_OUT"
}

10. GET /api/stats/amount-distribution

Description: Histogram of transaction amounts (value bins)

Response:

{
  "bins": ["0-100", "100-500", "500-1000", "1000-5000"],
  "counts": [10000, 53000, 42000, 21000]
}

11. GET /api/stats/by-type

Description: Total amount and average transaction count per type

Response:

[
  { "type": "PAYMENT", "count": 1250000, "avg_amount": 350.21 },
  { "type": "TRANSFER", "count": 400000, "avg_amount": 13000.58 }
]

12. GET /api/stats/daily

Description: Daily average and transaction volume (step-based)

Fraud
13. GET /api/fraud/summary

Description: Fraud overview

Response:

{
  "total_frauds": 8213,
  "flagged": 16,
  "precision": 0.95,
  "recall": 0.88
}

14. GET /api/fraud/by-type

Description: Fraud rate distribution by transaction type

15. POST /api/fraud/predict

Description: Scoring endpoint to predict fraud

Request body:

{
  "type": "TRANSFER",
  "amount": 3500.0,
  "oldbalanceOrg": 15000.0,
  "newbalanceOrig": 11500.0
}


Response:

{
  "isFraud": true,
  "probability": 0.89
}

Customers
16. GET /api/customers

Description: Paginated list of customers (from nameOrig)

17. GET /api/customers/{customer_id}

Description: Synthetic customer profile

Response:

{
  "id": "C1231006815",
  "transactions_count": 58,
  "avg_amount": 205.33,
  "fraudulent": false
}

18. GET /api/customers/top

Description: Top customers ranked by total transaction volume
Parameter: n (default = 10)

System
19. GET /api/system/health

Description: API health check

Response:

{
  "status": "ok",
  "uptime": "2h 15min",
  "dataset_loaded": true
}

20. GET /api/system/metadata

Description: Service version and last update

Response:

{
  "version": "1.0.0",
  "last_update": "2025-12-20T22:00:00Z"
}

4. Internal Services
Service file	Role
transactions_service.py	Read, paginate, filter, multi-criteria search
stats_service.py	Aggregations and distributions
fraud_detection_service.py	Fraud rates and scoring
customer_service.py	Customer-level aggregation
system_service.py	Service diagnostics and metadata
5. Expected Unit Tests
Domain	Requirements
Routes	1 test per endpoint (≥ 20 tests)
Services	Tests for stats and fraud functions
Validation	JSON input format validation
Performance	Max latency < 500ms for 100 filtered transactions
Coverage	Target ≥ 85%
6. CI/CD and Packaging

Linting: flake8

Typing: mypy

Tests: pytest --cov

Tests: python -m unittest

Package build:

poetry build or python -m build

Alternative build using setuptools (as seen in class)