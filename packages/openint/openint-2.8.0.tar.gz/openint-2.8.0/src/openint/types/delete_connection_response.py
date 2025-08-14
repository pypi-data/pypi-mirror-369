# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["DeleteConnectionResponse"]


class DeleteConnectionResponse(BaseModel):
    id: str
    """The id of the connection, starts with `conn_`"""
