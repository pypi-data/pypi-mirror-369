# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Connector", "Schemas", "Scope"]


class Schemas(BaseModel):
    connect_input: Optional[object] = None

    connect_output: Optional[object] = None

    connection_settings: Optional[object] = None

    connector_config: Optional[object] = None

    integration_data: Optional[object] = None

    pre_connect_input: Optional[object] = None

    webhook_input: Optional[object] = None


class Scope(BaseModel):
    scope: str

    description: Optional[str] = None

    display_name: Optional[str] = None


class Connector(BaseModel):
    name: str

    auth_type: Optional[Literal["BASIC", "OAUTH1", "OAUTH2", "OAUTH2CC", "API_KEY", "CUSTOM"]] = None

    display_name: Optional[str] = None

    has_openint_credentials: Optional[bool] = None

    logo_url: Optional[str] = None

    openint_allowed_scopes: Optional[List[str]] = None

    openint_default_scopes: Optional[List[str]] = None

    platforms: Optional[List[Literal["web", "mobile", "desktop", "local", "cloud"]]] = None

    required_scopes: Optional[List[str]] = None

    schemas: Optional[Schemas] = None

    scopes: Optional[List[Scope]] = None

    stage: Optional[Literal["alpha", "beta", "ga", "hidden"]] = None
