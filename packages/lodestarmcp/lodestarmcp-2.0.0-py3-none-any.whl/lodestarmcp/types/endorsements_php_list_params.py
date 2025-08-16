# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .loan_info_param import LoanInfoParam

__all__ = ["EndorsementsPhpListParams"]


class EndorsementsPhpListParams(TypedDict, total=False):
    county: Required[str]
    """County name.

    If the LodeStar County endpoint was not used and the county is supplied from the
    users own list LodeStar will try to use fuzzy logic to match similar names (i.e.
    Saint Mary's vs St. Marys). Do not include the word County (i.e. Saint Marys
    County vs Saint Marys)
    """

    purpose: Required[str]
    """If a purpose has a leading zero it is required.

    There can be more options then the ones listed below. Can retrieve additional
    transaction types ids from transaction_ids endpoint. Please contact us if you
    require a different option Purpose Types:

    - `00` - Refinance
    - `04` - Refinance (Reissue)
    - `11` - Purchase
    """

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]
    """2 letter state abbreviation"""

    loan_info: LoanInfoParam
    """
    loan_info object as described in the schema component can be passed to add any
    additional endorsements based on a specific loan scenario.
    """

    sub_agent_id: float
    """This will only be used by lender's.

    This will allow for the selection of different related title agents.
    """

    sub_agent_office_id: float
    """This will only be used by lender's.

    This will allow for the selection of different related title agents offices (if
    any). Defaults to 1.
    """
