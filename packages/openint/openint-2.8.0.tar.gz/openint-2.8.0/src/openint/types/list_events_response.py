# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Union, Optional
from typing_extensions import Literal, TypeAlias

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "ListEventsResponse",
    "UnionMember0",
    "UnionMember1",
    "UnionMember1Data",
    "UnionMember2",
    "UnionMember3",
    "UnionMember4",
    "UnionMember4Data",
    "UnionMember5",
    "UnionMember5Data",
    "UnionMember6",
    "UnionMember7",
    "UnionMember8",
    "UnionMember8Data",
    "UnionMember9",
    "UnionMember9Data",
    "UnionMember10",
    "UnionMember10Data",
    "UnionMember11",
    "UnionMember11Data",
    "UnionMember12",
    "UnionMember13",
    "UnionMember13Data",
    "UnionMember14",
    "UnionMember14Data",
    "UnionMember15",
    "UnionMember15Data",
    "UnionMember16",
    "UnionMember16Data",
    "UnionMember17",
    "UnionMember18",
    "UnionMember19",
    "UnionMember20",
    "UnionMember20Data",
]


class UnionMember0(BaseModel):
    data: object

    name: Literal["debug.debug"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember1Data(BaseModel):
    headers: Dict[str, object]

    method: str

    path: str

    query: Dict[str, object]

    trace_id: str = FieldInfo(alias="traceId")

    body: Optional[object] = None


class UnionMember1(BaseModel):
    data: UnionMember1Data

    name: Literal["webhook.received"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember2(BaseModel):
    data: object

    name: Literal["db.user-created"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember3(BaseModel):
    data: object

    name: Literal["db.user-deleted"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember4Data(BaseModel):
    connection_id: str
    """Must start with 'conn\\__'"""


class UnionMember4(BaseModel):
    data: UnionMember4Data

    name: Literal["db.connection-created"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember5Data(BaseModel):
    connection_id: str
    """Must start with 'conn\\__'"""


class UnionMember5(BaseModel):
    data: UnionMember5Data

    name: Literal["db.connection-deleted"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember6(BaseModel):
    data: object

    name: Literal["user.signin"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember7(BaseModel):
    data: object

    name: Literal["user.signout"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember8Data(BaseModel):
    connector_name: str

    meta: Optional[object] = None


class UnionMember8(BaseModel):
    data: UnionMember8Data

    name: Literal["connect.session-started"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember9Data(BaseModel):
    connector_name: str

    meta: Optional[object] = None


class UnionMember9(BaseModel):
    data: UnionMember9Data

    name: Literal["connect.session-cancelled"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember10Data(BaseModel):
    connector_name: str

    meta: Optional[object] = None


class UnionMember10(BaseModel):
    data: UnionMember10Data

    name: Literal["connect.session-succeeded"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember11Data(BaseModel):
    connector_name: str

    meta: Optional[object] = None


class UnionMember11(BaseModel):
    data: UnionMember11Data

    name: Literal["connect.session-errored"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember12(BaseModel):
    data: object

    name: Literal["connect.loaded"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember13Data(BaseModel):
    error_details: Optional[str] = None

    error_message: Optional[str] = None


class UnionMember13(BaseModel):
    data: UnionMember13Data

    name: Literal["connect.loading-error"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember14Data(BaseModel):
    connection_id: str
    """Must start with 'conn\\__'"""

    customer_id: Optional[str] = None


class UnionMember14(BaseModel):
    data: UnionMember14Data

    name: Literal["connect.connection-connected"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember15Data(BaseModel):
    connection_id: str
    """Must start with 'conn\\__'"""

    customer_id: str


class UnionMember15(BaseModel):
    data: UnionMember15Data

    name: Literal["connect.connection-deleted"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember16Data(BaseModel):
    connection_id: str
    """Must start with 'conn\\__'"""

    customer_id: str

    status: Optional[str] = None

    status_message: Optional[str] = None


class UnionMember16(BaseModel):
    data: UnionMember16Data

    name: Literal["connect.connection-checked"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember17(BaseModel):
    data: object

    name: Literal["api.token-copied"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember18(BaseModel):
    data: object

    name: Literal["api.graphql-request"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember19(BaseModel):
    data: object

    name: Literal["api.rest-request"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


class UnionMember20Data(BaseModel):
    current_url: str

    path: str


class UnionMember20(BaseModel):
    data: UnionMember20Data

    name: Literal["pageview"]

    id: Optional[str] = None

    customer_id: Optional[str] = None

    org_id: Optional[str] = None

    prompt: Optional[str] = None

    timestamp: Optional[str] = None

    user: Union[str, float, bool, Dict[str, object], List[object], None] = None

    user_id: Optional[str] = None

    v: Optional[str] = None


ListEventsResponse: TypeAlias = Union[
    UnionMember0,
    UnionMember1,
    UnionMember2,
    UnionMember3,
    UnionMember4,
    UnionMember5,
    UnionMember6,
    UnionMember7,
    UnionMember8,
    UnionMember9,
    UnionMember10,
    UnionMember11,
    UnionMember12,
    UnionMember13,
    UnionMember14,
    UnionMember15,
    UnionMember16,
    UnionMember17,
    UnionMember18,
    UnionMember19,
    UnionMember20,
]
