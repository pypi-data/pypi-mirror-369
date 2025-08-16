# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["PropertyTaxPhpRetrieveParams"]


class PropertyTaxPhpRetrieveParams(TypedDict, total=False):
    address: Required[str]

    city: Required[str]

    close_date: Required[Annotated[Union[str, date], PropertyInfo(format="iso8601")]]

    county: Required[str]
    """County name.

    If the LodeStar County endpoint was not used and the county is supplied from the
    users own list LodeStar will try to use fuzzy logic to match similar names (i.e.
    Saint Mary's vs St. Marys). Do not include the word County (i.e. Saint Marys
    County vs Saint Marys)
    """

    file_name: Required[str]

    purchase_price: Required[float]
    """
    The purchase price or market value of the property is required for the
    calculation of the estiamted property taxes if no property tax record can be
    found.
    """

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]
    """2 letter state abbreviation"""
