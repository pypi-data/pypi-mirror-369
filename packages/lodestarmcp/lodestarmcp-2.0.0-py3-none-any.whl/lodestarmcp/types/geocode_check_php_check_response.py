# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["GeocodeCheckPhpCheckResponse"]


class GeocodeCheckPhpCheckResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means the check was properly run"""

    message: Optional[str] = None
    """Only returned if there is an error."""

    suggested_county: Optional[str] = None

    suggested_township: Optional[str] = None

    township_options: Optional[List[str]] = None
