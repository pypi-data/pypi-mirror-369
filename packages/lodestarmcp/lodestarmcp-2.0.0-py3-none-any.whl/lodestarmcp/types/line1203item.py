# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Line1203item"]


class Line1203item(BaseModel):
    amount: Optional[float] = None

    jur: Optional[Literal["City", "County", "State"]] = None

    type: Optional[str] = None
    """Descriptor for type of tax.

    Usually document name + Tax but can be different. i.e. GrantorTax in VA.
    Examples - 'MortgageTax' - 'MortgageRecordationTax'
    """
