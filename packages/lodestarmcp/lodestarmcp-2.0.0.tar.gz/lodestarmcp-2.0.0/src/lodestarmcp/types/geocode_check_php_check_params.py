# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["GeocodeCheckPhpCheckParams"]


class GeocodeCheckPhpCheckParams(TypedDict, total=False):
    address: Required[str]

    county: Required[str]
    """County name.

    If the LodeStar County endpoint was not used and the county is supplied from the
    users own list LodeStar will try to use fuzzy logic to match similar names (i.e.
    Saint Mary's vs St. Marys). Do not include the word County (i.e. Saint Marys
    County vs Saint Marys)
    """

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]
    """2 letter state abbreviation"""

    township: Required[str]
