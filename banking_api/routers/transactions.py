"""Transaction routes (Routes 1-8).

This module defines the API endpoints for transaction operations.
"""
from typing import Optional

from fastapi import APIRouter, Query, Request

from banking_api.models.responses import DeleteResponse, TransactionListResponse
from banking_api.models.transaction import SearchRequest, Transaction
from banking_api.services import transactions_service

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    type: Optional[str] = Query(None, description="Filter by transaction type"),
    isFraud: Optional[int] = Query(None, ge=0, le=1, description="Filter by fraud status"),
    min_amount: Optional[float] = Query(None, ge=0, description="Minimum amount"),
    max_amount: Optional[float] = Query(None, ge=0, description="Maximum amount"),
) -> TransactionListResponse:
    """Get paginated list of transactions.

    Route 1: GET /api/transactions

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    page : int
        Page number (1-indexed).
    limit : int
        Number of items per page.
    type : str, optional
        Filter by transaction type.
    isFraud : int, optional
        Filter by fraud status (0 or 1).
    min_amount : float, optional
        Minimum transaction amount.
    max_amount : float, optional
        Maximum transaction amount.

    Returns
    -------
    TransactionListResponse
        Paginated list of transactions.
    """
    transactions, _ = transactions_service.get_transactions(
        request,
        page=page,
        limit=limit,
        type_filter=type,
        is_fraud=isFraud,
        min_amount=min_amount,
        max_amount=max_amount
    )

    # Convert to summary format for list response
    summary_list = [
        {"id": t["id"], "amount": t["amount"], "type": t["type"]}
        for t in transactions
    ]

    return TransactionListResponse(page=page, transactions=summary_list)


@router.get("/types", response_model=list[str])
def get_transaction_types(request: Request) -> list[str]:
    """Get list of available transaction types.

    Route 4: GET /api/transactions/types

    Parameters
    ----------
    request : Request
        The FastAPI request object.

    Returns
    -------
    list[str]
        List of unique transaction types.
    """
    return transactions_service.get_transaction_types(request)


@router.get("/recent", response_model=list[Transaction])
def get_recent_transactions(
    request: Request,
    n: int = Query(10, ge=1, le=100, description="Number of transactions")
) -> list[Transaction]:
    """Get the N most recent transactions.

    Route 5: GET /api/transactions/recent

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    n : int
        Number of transactions to return.

    Returns
    -------
    list[Transaction]
        List of recent transactions.
    """
    transactions = transactions_service.get_recent_transactions(request, n)
    return [Transaction(**t) for t in transactions]


@router.get("/by-customer/{customer_id}", response_model=list[Transaction])
def get_transactions_by_customer(
    request: Request,
    customer_id: str
) -> list[Transaction]:
    """Get transactions sent by a customer (as origin).

    Route 7: GET /api/transactions/by-customer/{customer_id}

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    customer_id : str
        The customer identifier.

    Returns
    -------
    list[Transaction]
        List of transactions where customer is the sender.
    """
    transactions = transactions_service.get_transactions_by_customer(
        request, customer_id, as_origin=True
    )
    return [Transaction(**t) for t in transactions]


@router.get("/to-customer/{customer_id}", response_model=list[Transaction])
def get_transactions_to_customer(
    request: Request,
    customer_id: str
) -> list[Transaction]:
    """Get transactions received by a customer (as destination).

    Route 8: GET /api/transactions/to-customer/{customer_id}

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    customer_id : str
        The customer identifier.

    Returns
    -------
    list[Transaction]
        List of transactions where customer is the recipient.
    """
    transactions = transactions_service.get_transactions_by_customer(
        request, customer_id, as_origin=False
    )
    return [Transaction(**t) for t in transactions]


@router.get("/{id}", response_model=Transaction)
def get_transaction(request: Request, id: str) -> Transaction:
    """Get transaction details by ID.

    Route 2: GET /api/transactions/{id}

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    id : str
        The unique transaction identifier.

    Returns
    -------
    Transaction
        Transaction details.

    Raises
    ------
    HTTPException
        404 if transaction not found.
    """
    transaction = transactions_service.get_transaction_by_id(request, id)
    return Transaction(**transaction)


@router.post("/search", response_model=list[Transaction])
def search_transactions(
    request: Request,
    criteria: SearchRequest
) -> list[Transaction]:
    """Search transactions using multiple criteria.

    Route 3: POST /api/transactions/search

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    criteria : SearchRequest
        Search criteria including type, isFraud, amount_range.

    Returns
    -------
    list[Transaction]
        List of matching transactions (limited to 100).
    """
    search_dict = criteria.model_dump(exclude_none=True)
    transactions = transactions_service.search_transactions(request, search_dict)
    return [Transaction(**t) for t in transactions]


@router.delete("/{id}", response_model=DeleteResponse)
def delete_transaction(request: Request, id: str) -> DeleteResponse:
    """Delete a transaction (test mode only).

    Route 6: DELETE /api/transactions/{id}

    This endpoint is only available when TEST_MODE=1 is set.
    In production mode, it returns a 403 Forbidden error.

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    id : str
        The unique transaction identifier.

    Returns
    -------
    DeleteResponse
        Deletion confirmation.

    Raises
    ------
    HTTPException
        403 if not in test mode.
        404 if transaction not found.
    """
    transactions_service.delete_transaction(request, id)
    return DeleteResponse(
        success=True,
        message=f"Transaction {id} deleted successfully"
    )
