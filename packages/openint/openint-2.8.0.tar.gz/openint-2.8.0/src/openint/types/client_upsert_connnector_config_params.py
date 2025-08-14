# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import TypedDict

__all__ = ["ClientUpsertConnnectorConfigParams"]


class ClientUpsertConnnectorConfigParams(TypedDict, total=False):
    config: Optional[Dict[str, object]]

    disabled: bool

    display_name: str
