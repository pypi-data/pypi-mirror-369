# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = ["QuestionsPhpGetQuestionsResponse", "QuestionsPhpGetQuestionsResponseItem"]


class QuestionsPhpGetQuestionsResponseItem(BaseModel):
    categories: Optional[List[str]] = None
    """
    A string represenation of the type of question to allow for
    inter-state/inter-transaction question mapping. > For example in a state that
    has the following question 'Is the Lender a Federal Credit Union?' it will have
    the categories federal_credit_union Another example would be for the following
    question 'Is the borrower a qualified First Time Home Buyer and is the property
    a principal residency?' would have the following categories first_time,
    principal
    """

    default_value: Union[str, bool, float, None] = None
    """default value for the question answer."""

    input_type: Optional[Literal["checkbox", "number", "text"]] = None
    """Suggested user facing input type."""

    label: Optional[str] = None
    """User facing text description of the question."""

    name: Optional[str] = None
    """Name/Key of the parameter/property."""

    related_doc: Optional[Literal["deed", "mort", "release", "att", "assign", "sub", "mod"]] = None
    """If the question is related to a specific document.

    Possible values Document Types:

    - `deed` - Deed
    - `mort` - Mortgage/Deed Of Trust
    - `release` - Release of Real Estate Lien
    - `att` - Power Of Attorney
    - `assign` - Assignment
    - `sub` - Subordination
    - `mod` - Modification
    """

    value_type: Optional[Literal["boolean", "number", "percent", "date"]] = None
    """Expected type of response to question. Purpose Types:

    - `boolean` - true or false value
    - `number` - Double value
    - `percent` - Double value with a max of 100"
    - `date` - text date value in the format yyyy-mm-dd
    """


QuestionsPhpGetQuestionsResponse: TypeAlias = List[QuestionsPhpGetQuestionsResponseItem]
