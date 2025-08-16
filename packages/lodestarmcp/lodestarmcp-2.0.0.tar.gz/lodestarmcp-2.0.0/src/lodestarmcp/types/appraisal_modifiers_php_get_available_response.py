# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["AppraisalModifiersPhpGetAvailableResponse", "AppMod"]


class AppMod(BaseModel):
    id: float
    """Modifier ID.

    This will be passed to either the closing_cost_calculations endpoint or the
    appraisal_calculate endpoint.
    """

    name: str
    """Modifier name that can be displayed to an end user."""


class AppraisalModifiersPhpGetAvailableResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    app_mods: Optional[List[AppMod]] = None

    message: Optional[str] = None
    """Only returned if there is no result found."""
