# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["LoanInfoParam"]


class LoanInfoParam(TypedDict, total=False):
    amort_type: Literal[1, 2]
    """
    Optional property that describes what type of amortization scheudule is used for
    the loan . Amort Types:

    - `1` - Fixed Rate
    - `2` - Adjustable Rate
    """

    is_federal_credit_union: Literal[0, 1]
    """Is the lender a federal credit union. Possible Values:

    - `0` - False
    - `1` - True
    """

    is_first_time_home_buyer: Literal[0, 1]
    """Is the borrower(s) a first time home buyer? Possible Values:

    - `0` - False
    - `1` - True
    """

    is_same_borrwers_as_previous: Literal[0, 1]
    """
    Is the borrower(s) on the new mortgage the same as borrower(s) as on the
    original mortgage. Possible Values:

    - `0` - False
    - `1` - True
    """

    is_same_lender_as_previous: Literal[0, 1]
    """Is the lender on the new mortgage the same as lender as on the original
    mortgage.

    Possible Values:

    - `0` - False
    - `1` - True
    """

    loan_type: Literal[1, 2, 3, 4, 5, 6]
    """Optional property that describes what type of loan program is being used.

    Loan Types:

    - `1` - Conventional
    - `2` - FHA
    - `3` - VA
    - `4` - USDA
    """

    number_of_families: int
    """Number of Families that the property is zoned for."""

    prop_purpose: Literal[1, 2, 3]
    """Optional property that describes what the property will be used for.

    Property Propse Types:

    - `1` - Primary
    - `2` - Secondary
    - `3` - Investment
    """

    prop_type: Literal[1, 2, 3, 4, 5, 6, 7]
    """Optional property that describes what type of subject property is being run.

    Prop Types:

    - `1` - Single Family
    - `2` - Multi Family
    - `3` - Condo
    - `4` - Coop
    - `5` - PUD
    - `6` - Manufactured
    - `7` - Land
    """

    prop_usage: Literal[1, 2, 3]
    """Property Planned Usage/Zoning Property Usage Types:

    - `1` - Residential
    - `2` - Commericial
    - `3` - Mixed-use
    """
