# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["LoginAuthenticateResponse"]


class LoginAuthenticateResponse(BaseModel):
    session_id: Optional[str] = None
    """This is the session token that will need to be passed to all other endpoints"""

    success: Optional[str] = None
