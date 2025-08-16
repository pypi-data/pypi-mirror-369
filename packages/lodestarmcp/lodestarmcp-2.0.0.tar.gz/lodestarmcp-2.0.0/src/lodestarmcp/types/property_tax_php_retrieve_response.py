# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = [
    "PropertyTaxPhpRetrieveResponse",
    "Assessment",
    "Calculations",
    "TaxCalendar",
    "TaxCalendarFullCal",
    "TaxCalendarNextDue",
    "TaxCalendarPrevDue",
]


class Assessment(BaseModel):
    tax_amount: Optional[float] = None
    """How much was the property tax was paid on the property"""

    tax_year: Optional[float] = None
    """Year that this record is for."""


class Calculations(BaseModel):
    escrow_amount: Optional[float] = None
    """Total amount due for escrow"""

    escrow_due_days: Optional[int] = None
    """Days due for escrow"""

    escrow_due_months: Optional[int] = None
    """Months due for escrow"""

    tax_per_month: Optional[float] = None
    """Tax paid per month"""


class TaxCalendarFullCal(BaseModel):
    date: Optional[str] = None
    """Date of property tax due date in mm-dd format"""


class TaxCalendarNextDue(BaseModel):
    date: Optional[str] = None
    """Date of next due date in yyyy-mm-dd format"""

    diff: Optional[float] = None
    """Difference in days between passed closing_date and the next payment.

    Accounts for leap days.
    """


class TaxCalendarPrevDue(BaseModel):
    date: Optional[str] = None
    """Date of previous due date in yyyy-mm-dd format"""

    diff: Optional[float] = None
    """Difference in days between passed closing_date and the previous payment.

    Accounts for leap days.
    """


class TaxCalendar(BaseModel):
    full_cal: Optional[List[TaxCalendarFullCal]] = None
    """Aray of property tax due dates in mm-dd format.

    Dates are last payment dates and do not include early discount dates.
    """

    next_due: Optional[TaxCalendarNextDue] = None

    prev_due: Optional[TaxCalendarPrevDue] = None


class PropertyTaxPhpRetrieveResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    assessments: Optional[List[Assessment]] = None

    calculations: Optional[Calculations] = None
    """Calculated values using the retrieved values of tax amount and calendar dates"""

    message: Optional[str] = None
    """Only returned if there is no result found."""

    response_details: Optional[Literal["TBDAddress", "AddressNotFound", "AddressFound"]] = None

    tax_calendar: Optional[TaxCalendar] = None
