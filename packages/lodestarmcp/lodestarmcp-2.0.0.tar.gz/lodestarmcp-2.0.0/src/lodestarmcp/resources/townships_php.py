# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import townships_php_get_available_townships_params
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
from ..types.townships_php_get_available_townships_response import TownshipsPhpGetAvailableTownshipsResponse

__all__ = ["TownshipsPhpResource", "AsyncTownshipsPhpResource"]


class TownshipsPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TownshipsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return TownshipsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TownshipsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return TownshipsPhpResourceWithStreamingResponse(self)

    def get_available_townships(
        self,
        *,
        county: str,
        session_id: str,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TownshipsPhpGetAvailableTownshipsResponse:
        """Get available townships in a county for les_engine calls.

        If all townships have
        the same fees then there will only be an All Townships option. If there are
        multiple townships avialble there will also be an All Other Townships option
        available to cover not listened options. Please request that this functionality
        be turned on.

        Args:
          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/townships.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "county": county,
                        "session_id": session_id,
                        "state": state,
                    },
                    townships_php_get_available_townships_params.TownshipsPhpGetAvailableTownshipsParams,
                ),
            ),
            cast_to=TownshipsPhpGetAvailableTownshipsResponse,
        )


class AsyncTownshipsPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTownshipsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncTownshipsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTownshipsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncTownshipsPhpResourceWithStreamingResponse(self)

    async def get_available_townships(
        self,
        *,
        county: str,
        session_id: str,
        state: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> TownshipsPhpGetAvailableTownshipsResponse:
        """Get available townships in a county for les_engine calls.

        If all townships have
        the same fees then there will only be an All Townships option. If there are
        multiple townships avialble there will also be an All Other Townships option
        available to cover not listened options. Please request that this functionality
        be turned on.

        Args:
          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/townships.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "county": county,
                        "session_id": session_id,
                        "state": state,
                    },
                    townships_php_get_available_townships_params.TownshipsPhpGetAvailableTownshipsParams,
                ),
            ),
            cast_to=TownshipsPhpGetAvailableTownshipsResponse,
        )


class TownshipsPhpResourceWithRawResponse:
    def __init__(self, townships_php: TownshipsPhpResource) -> None:
        self._townships_php = townships_php

        self.get_available_townships = to_raw_response_wrapper(
            townships_php.get_available_townships,
        )


class AsyncTownshipsPhpResourceWithRawResponse:
    def __init__(self, townships_php: AsyncTownshipsPhpResource) -> None:
        self._townships_php = townships_php

        self.get_available_townships = async_to_raw_response_wrapper(
            townships_php.get_available_townships,
        )


class TownshipsPhpResourceWithStreamingResponse:
    def __init__(self, townships_php: TownshipsPhpResource) -> None:
        self._townships_php = townships_php

        self.get_available_townships = to_streamed_response_wrapper(
            townships_php.get_available_townships,
        )


class AsyncTownshipsPhpResourceWithStreamingResponse:
    def __init__(self, townships_php: AsyncTownshipsPhpResource) -> None:
        self._townships_php = townships_php

        self.get_available_townships = async_to_streamed_response_wrapper(
            townships_php.get_available_townships,
        )
