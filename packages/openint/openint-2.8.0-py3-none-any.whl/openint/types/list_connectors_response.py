# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .connector import Connector
from .integration import Integration

__all__ = ["ListConnectorsResponse"]


class ListConnectorsResponse(Connector):
    integrations: Optional[List[Integration]] = None
