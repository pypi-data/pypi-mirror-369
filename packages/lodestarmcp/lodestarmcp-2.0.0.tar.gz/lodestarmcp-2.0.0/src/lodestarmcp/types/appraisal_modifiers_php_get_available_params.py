# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["AppraisalModifiersPhpGetAvailableParams"]


class AppraisalModifiersPhpGetAvailableParams(TypedDict, total=False):
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

    loan_info_amort_type: Annotated[int, PropertyInfo(alias="loan_info[amort_type]")]
    """
    Optional property that describes what type of amortization scheudule is used for
    the loan . Amort Types:

    - `1` - Fixed Rate
    - `2` - Adjustable Rate
    """

    loan_info_loan_type: Annotated[int, PropertyInfo(alias="loan_info[loan_type]")]
    """
    Optional property that describes what type of loan program is being used. Loan
    Types:

    - `1` - Conventional
    - `2` - FHA
    - `3` - VA
    - `4` - USDA
    """

    loan_info_prop_type: Annotated[int, PropertyInfo(alias="loan_info[prop_type]")]
    """
    Optional property that describes what type of subject property is being run.
    Prop Types:

    - `1` - Single Family
    - `2` - Multi Family
    - `3` - Condo
    - `4` - Coop
    - `5` - PUD
    - `6` - Manufactured
    - `7` - Land example: 1
    """
