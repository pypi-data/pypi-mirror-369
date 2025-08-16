# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["QuestionsPhpGetQuestionsParams"]


class QuestionsPhpGetQuestionsParams(TypedDict, total=False):
    purpose: Required[Literal["00", "11", "04"]]
    """If a purpose has a leading zero it is required.

    There can be more options then the ones listed below. Please contact us if you
    require a different option Purpose Types:

    - `00` - Refinance
    - `04` - Refinance (Reissue)
    - `11` - Purchase
    """

    session_id: Required[str]
    """The string returned from the `LOGIN /Login/login.php` method"""

    state: Required[str]
    """2 letter state abbreviation"""
