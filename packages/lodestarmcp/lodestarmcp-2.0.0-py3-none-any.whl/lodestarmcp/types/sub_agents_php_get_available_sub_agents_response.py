# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = [
    "SubAgentsPhpGetAvailableSubAgentsResponse",
    "SubAgentResponseWithContactInfo",
    "SubAgentResponseWithContactInfoSubAgent",
    "SubAgentResponseWithContactInfoSubAgentContactInfo",
    "SubAgentResponse",
    "SubAgentResponseSubAgent",
]


class SubAgentResponseWithContactInfoSubAgentContactInfo(BaseModel):
    address: str
    """Office address"""

    city: str
    """Office city"""

    client_name: str
    """Company name"""

    contact_name: str
    """Branch Name"""

    is_multi_office: int
    """
    - `1` - Contact info is dynamic and will change depending on the location of the
      property. Closest office in the same state is returned. \\** `0` - Static
      contact info.
    """

    phone: str
    """Phone number of branch"""

    state: str
    """Two letter state abbreviation"""

    zip: str
    """5 digit zip code"""


class SubAgentResponseWithContactInfoSubAgent(BaseModel):
    relation_type: float
    """
    Sub Agents can provide different services or handle different parts of the
    closing process Relationship Types: _ `1` - Full service title agent. Provides
    closing/settlement/escrow services and title insurance. No other agent is
    necessary for a closing. _ `2` - Only provides closing/settlement/escrow
    service. A Title agent would be necessary. \\** `4` - Title only. An
    escrow/closing/settlement agent will also be necessary.
    """

    sub_agent_id: float
    """Sub Agent ID (for some endpoints can also be the client_id)."""

    sub_agent_office_id: float
    """Sub Agent Office ID.

    (for some endpoints can also be the agent_id). Usually 1 and will default to 1
    on most endpoint calls. However this can be used if multiple offices are setup
    for a title agent with different pricing.
    """

    contact_info: Optional[SubAgentResponseWithContactInfoSubAgentContactInfo] = None
    """Contact Info object for the sub agent"""

    name: Optional[str] = None
    """Agent Name.

    This is only used so the end user knows what endorsement is being selected.
    """


class SubAgentResponseWithContactInfo(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    message: Optional[str] = None
    """Only returned if there is an error found."""

    sub_agents: Optional[List[SubAgentResponseWithContactInfoSubAgent]] = None


class SubAgentResponseSubAgent(BaseModel):
    relation_type: float
    """
    Sub Agents can provide different services or handle different parts of the
    closing process Relationship Types: _ `1` - Full service title agent. Provides
    closing/settlement/escrow services and title insurance. No other agent is
    necessary for a closing. _ `2` - Only provides closing/settlement/escrow
    service. A Title agent would be necessary. \\** `4` - Title only. An
    escrow/closing/settlement agent will also be necessary.
    """

    sub_agent_id: float
    """Sub Agent ID (for some endpoints can also be the client_id)."""

    sub_agent_office_id: float
    """Sub Agent Office ID.

    (for some endpoints can also be the agent_id). Usually 1 and will default to 1
    on most endpoint calls. However this can be used if multiple offices are setup
    for a title agent with different pricing.
    """

    name: Optional[str] = None
    """Agent Name.

    This is only used so the end user knows what endorsement is being selected.
    """


class SubAgentResponse(BaseModel):
    status: float
    """0 means there was an issue. 1 means property tax have been retreived."""

    message: Optional[str] = None
    """Only returned if there is an error found."""

    sub_agents: Optional[List[SubAgentResponseSubAgent]] = None


SubAgentsPhpGetAvailableSubAgentsResponse: TypeAlias = Union[SubAgentResponseWithContactInfo, SubAgentResponse]
