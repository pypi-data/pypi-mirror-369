# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Line1201item"]


class Line1201item(BaseModel):
    amount: float

    jur: Literal["City", "County", "State"]
    """Which jurisidiction charges the recording fee"""

    type: object
    """Type of recording fee charged.

    Usually it will just be per document but it can sometimes be a state/county
    specific extra fee i.e. SB2 in California
    """
