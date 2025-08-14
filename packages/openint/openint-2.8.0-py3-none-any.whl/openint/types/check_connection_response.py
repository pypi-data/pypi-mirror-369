# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["CheckConnectionResponse"]


class CheckConnectionResponse(BaseModel):
    id: str

    status: Optional[Literal["healthy", "disconnected", "error", "manual", "unknown"]] = None

    status_message: Optional[str] = None
