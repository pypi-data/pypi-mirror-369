# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["EndorsementsPhpListResponse", "Endorsement"]


class Endorsement(BaseModel):
    default: float
    """
    Default does not mean that a quote ran thorugh les_engine will automatically
    include the endorsement. It means that by default the endorsement is requested
    so it should be in the requrested_endos array to les_engine 0 means that it is
    not normally quoted by default. 1 means it should be quoted by default.
    """

    endo_id: float
    """Endorsement ID. This will be passed to the les_engine request_endos array"""

    fee_id: float
    """LodeStar internal fee_id"""

    name: str
    """Endorsement name.

    This is only used so the end user knows what endorsement is being selected.
    """


class EndorsementsPhpListResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    endorsements: Optional[List[Endorsement]] = None

    message: Optional[str] = None
    """Only returned if there is no result found."""
