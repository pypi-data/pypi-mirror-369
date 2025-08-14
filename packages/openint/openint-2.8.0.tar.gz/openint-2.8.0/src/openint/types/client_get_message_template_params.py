# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ClientGetMessageTemplateParams"]


class ClientGetMessageTemplateParams(TypedDict, total=False):
    customer_id: Required[str]

    language: Literal["javascript"]

    use_environment_variables: bool
