# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional

from .._models import BaseModel

__all__ = ["UpsertCustomerResponse"]


class UpsertCustomerResponse(BaseModel):
    id: str

    api_key: Optional[str] = None

    created_at: str

    metadata: Union[str, float, bool, Dict[str, object], List[object], None] = None

    org_id: str

    updated_at: str
