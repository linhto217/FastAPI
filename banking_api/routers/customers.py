"""Customer routes (Routes 16-18).

This module defines the API endpoints for customer operations.
"""
from fastapi import APIRouter, Query, Request

from banking_api.models.customer import Customer, TopCustomer
from banking_api.models.responses import PaginatedResponse
from banking_api.services import customer_service

router = APIRouter(prefix="/api/customers", tags=["Customers"])


@router.get("", response_model=PaginatedResponse)
def list_customers(
    request: Request,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
) -> PaginatedResponse:
    """Get paginated list of customers.

    Route 16: GET /api/customers

    Customers are derived from the nameOrig field (transaction senders).

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    page : int
        Page number (1-indexed).
    limit : int
        Number of items per page.

    Returns
    -------
    PaginatedResponse
        Paginated list of customer IDs.
    """
    customers, total = customer_service.get_customers(request, page, limit)
    return PaginatedResponse(
        page=page,
        limit=limit,
        total=total,
        data=customers
    )


@router.get("/top", response_model=list[TopCustomer])
def get_top_customers(
    request: Request,
    n: int = Query(10, ge=1, le=100, description="Number of top customers")
) -> list[TopCustomer]:
    """Get top customers ranked by total transaction volume.

    Route 18: GET /api/customers/top

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    n : int
        Number of top customers to return.

    Returns
    -------
    list[TopCustomer]
        List of top customers with transaction statistics.
    """
    return customer_service.get_top_customers(request, n)


@router.get("/{customer_id}", response_model=Customer)
def get_customer(request: Request, customer_id: str) -> Customer:
    """Get synthetic customer profile.

    Route 17: GET /api/customers/{customer_id}

    Parameters
    ----------
    request : Request
        The FastAPI request object.
    customer_id : str
        The customer identifier.

    Returns
    -------
    Customer
        Customer profile with transaction statistics.

    Raises
    ------
    HTTPException
        404 if customer not found.
    """
    return customer_service.get_customer_by_id(request, customer_id)
