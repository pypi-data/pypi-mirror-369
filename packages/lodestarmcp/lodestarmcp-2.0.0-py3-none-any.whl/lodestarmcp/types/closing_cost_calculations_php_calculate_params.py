# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from datetime import date
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .document_param import DocumentParam
from .loan_info_param import LoanInfoParam

__all__ = ["ClosingCostCalculationsPhpCalculateParams", "DocType"]


class ClosingCostCalculationsPhpCalculateParams(TypedDict, total=False):
    county: Required[str]
    """County name.

    If the LodeStar County endpoint was not used and the county is supplied from the
    users own list LodeStar will try to use fuzzy logic to match similar names (i.e.
    Saint Mary's vs St. Marys). Do not include the word County (i.e. Saint Marys
    County vs Saint Marys)
    """

    purpose: Required[Literal["00", "11", "04"]]
    """If a purpose has a leading zero it is required.

    There can be more options then the ones listed below. Please contact us if you
    require a different option Purpose Types:

    - `00` - Refinance
    - `04` - Refinance (Reissue)
    - `11` - Purchase
    """

    search_type: Required[Literal["CFPB", "Title"]]
    """Controls what type of response data is needed Purpose Types:

    - `CFPB` - Returns tax, recording fees, title fees and title premiums.
    - `Title` - Title fees and title premiums only.
    """

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]

    township: Required[str]

    address: str

    agent_id: int
    """# Optional Calculation Parameter

    Sub Agent office id that specifies which office for a title Title Agent/Escrow
    Agent to use. Very frequently agent_id of 1 should be used. Only used for
    Originator Setups. Values is pulled from the sub_agent end point
    sub_agent_office_id value.'
    """

    app_mods: Iterable[int]
    """# Optional Calculation Parameter If Appraisal Calculations Requested

    Array of appraisal modifications that shoul be added to appraisal. List of
    possibile appraisal modifications can be retreived from appraisal_modifiers
    endpoint.
    """

    client_id: int
    """# Optional Calculation Parameter

    Sub Agent id that specifies which Title Agent/Escrow Agent to use. Only used for
    Originator Setups. Values is pulled from the sub_agent end point sub_agent_id
    value.'
    """

    close_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]

    doc_type: DocType
    """# Optional Calculation Parameter

    Contains which doucments need to be caluclated for the transaction. Document
    Types:

    - `deed` - Deed
    - `mort` - Mortgage/Deed Of Trust
    - `release` - Release of Real Estate Lien
    - `att` - Power Of Attorney
    - `assign` - Assignment
    - `sub` - Subordination
    - `mod` - Modification
    """

    exdebt: float
    """# For Refinance Quotes Only

    # Optional Calculation Parameter

    Parameter that is used for some refinance calulcations. The Questions endpoint
    will define if this field is needed.
    """

    filename: str
    """The unique file/loan name that the quote will be made for.

    This file name can be used for billing, tracking, and retrieval purposes.
    """

    include_appraisal: int
    """
    ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL APPRAISAL CHARGE # Optional Output Parameter

    Will include the appraisal calculations. This also provides the advantage of
    having the appraisal fee include in the PDF output. \\** `1` - Will include the
    appraisal calculations.
    """

    include_full_policy_amount: int
    """# Optional Output Parameter

    If full policy amount breakdowns are needed. This will mostly only be used by
    title agents. \\** `1` - Will return the breakdown
    """

    include_payee_info: int
    """# Optional Output Parameter

    Will return payee info for all title_agent_fees, transfer_taxes, and
    recording_fees. \\** `1` - Will return the breakdown
    """

    include_pdf: int
    """# Optional Output Parameter

    Will return PDF of the results mirrroring the LodeStar PDF output. \\** `1` - Will
    return the breakdown
    """

    include_property_tax: int
    """
    ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL PROPERTY TAX CHARGE # Optional Output Parameter

    Will include the property tax calculations for the property instead of having to
    call the property_tax endpoint separately. This also provides the advantage of
    having the property taxes include in the PDF output. \\** `1` - Will include the
    property tax calculations.
    """

    include_section: int
    """# Optional Output Parameter

    Will return what section in the LE/CD should the returned title agent and lender
    fees go into. \\** `1` - Will return the breakdown
    """

    include_seller_responsible: int
    """# Optional Output Parameter

    Will add a property (seller_responsible) on the seller paid taxes that will be a
    boolean value indicating if the tax should be marked as seller responsible. \\**
    `1` - Will return additional property.
    """

    int_name: str
    """A name to identify which integration is being used to make the request.

    Please ask LodeStar what this variable should be set to. If this is not properly
    set request might not be properly handled.
    """

    loan_amount: float
    """Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed."""

    loan_info: LoanInfoParam

    loanpol_level: Literal[1, 2]
    """# Optional Calculation Parameter

    Loan Policy Level. For Title Agent use only. Document Types:

    - `1` - Standard Policy
    - `2` - Enhanced
    """

    owners_level: Literal[1, 2]
    """# Optional Calculation Parameter

    Owners Policy Level. For Title Agent use only. Document Types:

    - `1` - Standard Policy
    - `2` - Enhanced
    """

    prior_insurance: float
    """# For Refinance Quotes Only

    # Optional Calculation Parameter

    Optional input that is used for some refinance calulcations. The Questions
    endpoint will define if this field is needed.
    """

    prior_insurance_date: Annotated[Union[str, date], PropertyInfo(format="iso8601")]
    """
    This date is only useful for refinances when a reissue discount is being looked
    for. It represents the date of the previous insurance policy effective date
    (usually the previous mortgage policy close date)
    """

    purchase_price: float
    """Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed."""

    qst: Dict[str, str]
    """# Optional Calculation Parameter

    Additional questions that can be answered. They are usually in the form of Q1
    => 1. However they can be more complex such as original_mort_date =>
    '01/10/2019'
    """

    request_endos: List[str]
    """# Optional Calculation Parameter

    Array of endorsements to get by ID. IDs can be retrieved from the endorsement
    endpoint. If endorsement endpoint is not available please contact support.
    """


class DocType(TypedDict, total=False):
    assign: DocumentParam

    att: DocumentParam

    deed: DocumentParam

    mod: DocumentParam

    mort: DocumentParam

    release: DocumentParam

    sub: DocumentParam
