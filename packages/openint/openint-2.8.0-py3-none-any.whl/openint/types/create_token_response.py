# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["CreateTokenResponse"]


class CreateTokenResponse(BaseModel):
    token: str
    """
    A short-lived publishable authentication token to use for customer api requests
    from the frontend. This token by default expires in 30 days unless otherwise
    specified via the validity_in_seconds parameter.
    """

    api_key: Optional[str] = None
    """A long-lived customer API key to use for API requests.

    Not meant to be published to the frontend.
    """

    magic_link_url: str
    """A link that can be shared with customers to use @Connect in any browser.

    This link will expire in 30 days by default unless otherwise specified via the
    validity_in_seconds parameter.
    """
