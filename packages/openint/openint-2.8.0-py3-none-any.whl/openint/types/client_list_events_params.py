# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientListEventsParams"]


class ClientListEventsParams(TypedDict, total=False):
    expand: List[Literal["prompt"]]

    limit: int
    """Limit the number of items returned"""

    offset: int
    """Offset the items returned"""

    search_query: str

    since: str
