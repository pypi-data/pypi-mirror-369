# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["LoginAuthenticateParams"]


class LoginAuthenticateParams(TypedDict, total=False):
    password: Required[str]
    """Password specific to the user"""

    username: Required[str]
    """Username to log into the system. Usually an email address"""
