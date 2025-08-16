# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TownshipsPhpGetAvailableTownshipsParams"]


class TownshipsPhpGetAvailableTownshipsParams(TypedDict, total=False):
    county: Required[str]

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: str
    """2 letter state abbreviation"""
