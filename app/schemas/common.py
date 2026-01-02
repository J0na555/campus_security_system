from pydantic import BaseModel
from typing import Optional, List

class SuccessResponse(BaseModel):
    status: str = "success"
    data: dict

class ErrorResponse(BaseModel):
    status: str = "error"
    code: str
    message: str
    details: Optional[List[dict]] = None

class PaginationInfo(BaseModel):
    currentPage: int
    totalPages: int
    totalItems: int
    itemsPerPage: int
    hasNextPage: bool
    hasPreviousPage: bool
