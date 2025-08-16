# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import endorsements_php_list_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.loan_info_param import LoanInfoParam
from ..types.endorsements_php_list_response import EndorsementsPhpListResponse

__all__ = ["EndorsementsPhpResource", "AsyncEndorsementsPhpResource"]


class EndorsementsPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EndorsementsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return EndorsementsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EndorsementsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return EndorsementsPhpResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        loan_info: LoanInfoParam | NotGiven = NOT_GIVEN,
        sub_agent_id: float | NotGiven = NOT_GIVEN,
        sub_agent_office_id: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndorsementsPhpListResponse:
        """Get available endorsements.

        The endo_id property can than be used when calling
        closing_cost_calculations.php in the request_endos object.

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Can retrieve additional transaction types ids from
              transaction_ids endpoint. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          loan_info: loan_info object as described in the schema component can be passed to add any
              additional endorsements based on a specific loan scenario.

          sub_agent_id: This will only be used by lender's. This will allow for the selection of
              different related title agents.

          sub_agent_office_id: This will only be used by lender's. This will allow for the selection of
              different related title agents offices (if any). Defaults to 1.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/endorsements.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "county": county,
                        "purpose": purpose,
                        "session_id": session_id,
                        "state": state,
                        "loan_info": loan_info,
                        "sub_agent_id": sub_agent_id,
                        "sub_agent_office_id": sub_agent_office_id,
                    },
                    endorsements_php_list_params.EndorsementsPhpListParams,
                ),
            ),
            cast_to=EndorsementsPhpListResponse,
        )


class AsyncEndorsementsPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEndorsementsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncEndorsementsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEndorsementsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncEndorsementsPhpResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        loan_info: LoanInfoParam | NotGiven = NOT_GIVEN,
        sub_agent_id: float | NotGiven = NOT_GIVEN,
        sub_agent_office_id: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EndorsementsPhpListResponse:
        """Get available endorsements.

        The endo_id property can than be used when calling
        closing_cost_calculations.php in the request_endos object.

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Can retrieve additional transaction types ids from
              transaction_ids endpoint. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          loan_info: loan_info object as described in the schema component can be passed to add any
              additional endorsements based on a specific loan scenario.

          sub_agent_id: This will only be used by lender's. This will allow for the selection of
              different related title agents.

          sub_agent_office_id: This will only be used by lender's. This will allow for the selection of
              different related title agents offices (if any). Defaults to 1.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/endorsements.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "county": county,
                        "purpose": purpose,
                        "session_id": session_id,
                        "state": state,
                        "loan_info": loan_info,
                        "sub_agent_id": sub_agent_id,
                        "sub_agent_office_id": sub_agent_office_id,
                    },
                    endorsements_php_list_params.EndorsementsPhpListParams,
                ),
            ),
            cast_to=EndorsementsPhpListResponse,
        )


class EndorsementsPhpResourceWithRawResponse:
    def __init__(self, endorsements_php: EndorsementsPhpResource) -> None:
        self._endorsements_php = endorsements_php

        self.list = to_raw_response_wrapper(
            endorsements_php.list,
        )


class AsyncEndorsementsPhpResourceWithRawResponse:
    def __init__(self, endorsements_php: AsyncEndorsementsPhpResource) -> None:
        self._endorsements_php = endorsements_php

        self.list = async_to_raw_response_wrapper(
            endorsements_php.list,
        )


class EndorsementsPhpResourceWithStreamingResponse:
    def __init__(self, endorsements_php: EndorsementsPhpResource) -> None:
        self._endorsements_php = endorsements_php

        self.list = to_streamed_response_wrapper(
            endorsements_php.list,
        )


class AsyncEndorsementsPhpResourceWithStreamingResponse:
    def __init__(self, endorsements_php: AsyncEndorsementsPhpResource) -> None:
        self._endorsements_php = endorsements_php

        self.list = async_to_streamed_response_wrapper(
            endorsements_php.list,
        )
