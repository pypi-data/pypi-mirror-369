# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["ClientListCustomersParams"]


class ClientListCustomersParams(TypedDict, total=False):
    limit: int
    """Limit the number of items returned"""

    offset: int
    """Offset the items returned"""

    search_query: Optional[str]
