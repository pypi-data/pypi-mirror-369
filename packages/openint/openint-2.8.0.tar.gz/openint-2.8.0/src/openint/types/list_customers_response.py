# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ListCustomersResponse"]


class ListCustomersResponse(BaseModel):
    id: Optional[str] = None
    """Customer Id"""

    connection_count: float

    created_at: str
    """postgres timestamp format, not yet ISO"""

    updated_at: str
    """postgres timestamp format, not yet ISO"""
