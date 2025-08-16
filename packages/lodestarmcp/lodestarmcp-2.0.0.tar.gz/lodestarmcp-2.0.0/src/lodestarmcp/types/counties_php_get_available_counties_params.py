# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CountiesPhpGetAvailableCountiesParams"]


class CountiesPhpGetAvailableCountiesParams(TypedDict, total=False):
    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]
    """2 letter state abbreviation"""
