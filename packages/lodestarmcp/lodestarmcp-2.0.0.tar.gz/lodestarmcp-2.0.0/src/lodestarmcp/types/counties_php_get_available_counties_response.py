# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["CountiesPhpGetAvailableCountiesResponse"]


class CountiesPhpGetAvailableCountiesResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    counties: Optional[List[str]] = None

    message: Optional[str] = None
    """Only returned if there is an error found."""
