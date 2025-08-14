# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, TypedDict

__all__ = ["ClientGetConectorConfigParams"]


class ClientGetConectorConfigParams(TypedDict, total=False):
    expand: List[Literal["connector", "connector.schemas", "connection_count"]]
