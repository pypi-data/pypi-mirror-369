# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Line1101item"]


class Line1101item(BaseModel):
    amount: Optional[float] = FieldInfo(alias="Amount", default=None)

    client_id: Optional[float] = FieldInfo(alias="ClientID", default=None)
    """The cooresponding agents client_id"""

    crfid: Optional[float] = FieldInfo(alias="CRFID", default=None)

    fee_type_id: Optional[str] = None
    """Enumeration for the type of fee:

    - `1` - Title
    - `2` - Escrow
    - `3` - Appraisal
    - `4` - Lender
    - `5` - Survey
    - `6` - Inspection
    - `7` - Pest
    """

    fee_name: Optional[str] = FieldInfo(alias="FeeName", default=None)
    """Standard Fee Names."""

    finance_charge: Optional[Literal["Y", "N"]] = FieldInfo(alias="FinanceCharge", default=None)
    """If Y then the fee is considered an APR charge."""

    mismo_map: Optional[object] = FieldInfo(alias="MismoMap", default=None)
    """Fee type as mapped to Mismo Map"""

    variable_name: Optional[str] = FieldInfo(alias="VariableName", default=None)
    """Fee Name."""
