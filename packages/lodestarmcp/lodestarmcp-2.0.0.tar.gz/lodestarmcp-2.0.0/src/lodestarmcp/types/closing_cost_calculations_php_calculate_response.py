# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel
from .line1101item import Line1101item
from .line1201item import Line1201item
from .line1203item import Line1203item

__all__ = [
    "ClosingCostCalculationsPhpCalculateResponse",
    "ClosingCostCalcultionsResponse",
    "ClosingCostCalcultionsResponseLoanPolicyPremium",
    "ClosingCostCalcultionsResponseOwnersPolicyPremium",
    "ClosingCostCalcultionsResponseTitleAgentFees",
    "ClosingCostCalcultionsResponseTransferTaxes",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputs",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsFullLoanPolicyPremium",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsFullOwnersPolicyPremium",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsLoanPolicyPremium",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsOwnersPolicyPremium",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsPdf",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsTitleAgentFees",
    "ClosingCostCalcultionsResponseWithAllOptionalOutputsTransferTaxes",
]


class ClosingCostCalcultionsResponseLoanPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid loan policy"""

    seller: Optional[float] = None
    """Seller paid loan policy"""


class ClosingCostCalcultionsResponseOwnersPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid owners policy"""

    seller: Optional[float] = None
    """Seller paid owners policy"""


class ClosingCostCalcultionsResponseTitleAgentFees(BaseModel):
    borrower: Optional[List[Line1101item]] = None
    """Array of borrower paid title fees"""

    seller: Optional[List[Line1101item]] = None
    """Array of seller paid title fees"""


class ClosingCostCalcultionsResponseTransferTaxes(BaseModel):
    borrower: Optional[List[List[Line1203item]]] = None
    """Array of borrower paid transfer taxes"""

    lender: Optional[List[List[Line1203item]]] = None
    """Array of lender paid transfer taxes"""

    seller: Optional[List[List[Line1203item]]] = None
    """Array of seller paid transfer taxes"""


class ClosingCostCalcultionsResponse(BaseModel):
    loan_policy_premium: Optional[ClosingCostCalcultionsResponseLoanPolicyPremium] = None
    """Lenders Policy calcualted in CFPB format. Information broken down by payer"""

    owners_policy_premium: Optional[ClosingCostCalcultionsResponseOwnersPolicyPremium] = None
    """Owners policy calcualted in CFPB format.

    Full Owners policy - Lenders policy + sim issue. Information broken down by
    payer
    """

    recording_fees: Optional[List[Line1201item]] = None
    """Buyer paid document recording fees."""

    search_id: Optional[float] = None

    simissue: Optional[float] = None
    """Sim issue for concurrent polcies"""

    title_agent_fees: Optional[ClosingCostCalcultionsResponseTitleAgentFees] = None
    """Object of title/settlement/escrow fees. Broken out by payer of the fees."""

    transfer_taxes: Optional[ClosingCostCalcultionsResponseTransferTaxes] = None


class ClosingCostCalcultionsResponseWithAllOptionalOutputsFullLoanPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid full loan policy"""

    seller: Optional[float] = None
    """Seller paid full loan policy"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsFullOwnersPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid full owners policy"""

    seller: Optional[float] = None
    """Seller paid full owners policy"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsLoanPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid loan policy"""

    seller: Optional[float] = None
    """Seller paid loan policy"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsOwnersPolicyPremium(BaseModel):
    borrower: Optional[float] = None
    """Borrower paid owners policy"""

    seller: Optional[float] = None
    """Seller paid owners policy"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsPdf(BaseModel):
    base64: Optional[str] = None
    """Base64 encoding of the results in the LodeStar PDF format."""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsTitleAgentFees(BaseModel):
    borrower: Optional[List[Line1101item]] = None
    """Array of borrower paid title fees"""

    seller: Optional[List[Line1101item]] = None
    """Array of seller paid title fees"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputsTransferTaxes(BaseModel):
    borrower: Optional[List[List[Line1203item]]] = None
    """Array of borrower paid transfer taxes"""

    lender: Optional[List[List[Line1203item]]] = None
    """Array of lender paid transfer taxes"""

    seller: Optional[List[List[Line1203item]]] = None
    """Array of seller paid transfer taxes"""


class ClosingCostCalcultionsResponseWithAllOptionalOutputs(BaseModel):
    full_loan_policy_premium: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsFullLoanPolicyPremium] = None
    """Lenders Policy calcualted as the sim issue fee."""

    full_owners_policy_premium: Optional[
        ClosingCostCalcultionsResponseWithAllOptionalOutputsFullOwnersPolicyPremium
    ] = None
    """Owners policy calcualted as the full owners policy."""

    loan_policy_premium: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsLoanPolicyPremium] = None
    """Lenders Policy calcualted in CFPB format. Information broken down by payer"""

    owners_policy_premium: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsOwnersPolicyPremium] = None
    """Owners policy calcualted in CFPB format.

    Full Owners policy - Lenders policy + sim issue. Information broken down by
    payer
    """

    pdf: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsPdf] = None

    recording_fees: Optional[List[Line1201item]] = None
    """Buyer paid document recording fees."""

    search_id: Optional[float] = None

    simissue: Optional[float] = None
    """Sim issue for concurrent polcies"""

    title_agent_fees: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsTitleAgentFees] = None
    """Object of title/settlement/escrow fees. Broken out by payer of the fees."""

    transfer_taxes: Optional[ClosingCostCalcultionsResponseWithAllOptionalOutputsTransferTaxes] = None


ClosingCostCalculationsPhpCalculateResponse: TypeAlias = Union[
    ClosingCostCalcultionsResponse, ClosingCostCalcultionsResponseWithAllOptionalOutputs
]
