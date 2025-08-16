# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, cast

import httpx

from ..types import sub_agents_php_get_available_sub_agents_params
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
from ..types.sub_agents_php_get_available_sub_agents_response import SubAgentsPhpGetAvailableSubAgentsResponse

__all__ = ["SubAgentsPhpResource", "AsyncSubAgentsPhpResource"]


class SubAgentsPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SubAgentsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return SubAgentsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubAgentsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return SubAgentsPhpResourceWithStreamingResponse(self)

    def get_available_sub_agents(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        address: str | NotGiven = NOT_GIVEN,
        get_contact_info: int | NotGiven = NOT_GIVEN,
        township: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SubAgentsPhpGetAvailableSubAgentsResponse:
        """
        Get available sub agents for a specific transaction type, state, and county.
        Please request that this functionality be turned on.

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

          get_contact_info: If contact info is required pass it as 1.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            SubAgentsPhpGetAvailableSubAgentsResponse,
            self._get(
                "/sub_agents.php",
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
                            "address": address,
                            "get_contact_info": get_contact_info,
                            "township": township,
                        },
                        sub_agents_php_get_available_sub_agents_params.SubAgentsPhpGetAvailableSubAgentsParams,
                    ),
                ),
                cast_to=cast(
                    Any, SubAgentsPhpGetAvailableSubAgentsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncSubAgentsPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSubAgentsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncSubAgentsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubAgentsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncSubAgentsPhpResourceWithStreamingResponse(self)

    async def get_available_sub_agents(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        address: str | NotGiven = NOT_GIVEN,
        get_contact_info: int | NotGiven = NOT_GIVEN,
        township: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SubAgentsPhpGetAvailableSubAgentsResponse:
        """
        Get available sub agents for a specific transaction type, state, and county.
        Please request that this functionality be turned on.

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

          get_contact_info: If contact info is required pass it as 1.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            SubAgentsPhpGetAvailableSubAgentsResponse,
            await self._get(
                "/sub_agents.php",
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
                            "address": address,
                            "get_contact_info": get_contact_info,
                            "township": township,
                        },
                        sub_agents_php_get_available_sub_agents_params.SubAgentsPhpGetAvailableSubAgentsParams,
                    ),
                ),
                cast_to=cast(
                    Any, SubAgentsPhpGetAvailableSubAgentsResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class SubAgentsPhpResourceWithRawResponse:
    def __init__(self, sub_agents_php: SubAgentsPhpResource) -> None:
        self._sub_agents_php = sub_agents_php

        self.get_available_sub_agents = to_raw_response_wrapper(
            sub_agents_php.get_available_sub_agents,
        )


class AsyncSubAgentsPhpResourceWithRawResponse:
    def __init__(self, sub_agents_php: AsyncSubAgentsPhpResource) -> None:
        self._sub_agents_php = sub_agents_php

        self.get_available_sub_agents = async_to_raw_response_wrapper(
            sub_agents_php.get_available_sub_agents,
        )


class SubAgentsPhpResourceWithStreamingResponse:
    def __init__(self, sub_agents_php: SubAgentsPhpResource) -> None:
        self._sub_agents_php = sub_agents_php

        self.get_available_sub_agents = to_streamed_response_wrapper(
            sub_agents_php.get_available_sub_agents,
        )


class AsyncSubAgentsPhpResourceWithStreamingResponse:
    def __init__(self, sub_agents_php: AsyncSubAgentsPhpResource) -> None:
        self._sub_agents_php = sub_agents_php

        self.get_available_sub_agents = async_to_streamed_response_wrapper(
            sub_agents_php.get_available_sub_agents,
        )
