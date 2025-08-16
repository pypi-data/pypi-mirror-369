# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import counties_php_get_available_counties_params
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
from ..types.counties_php_get_available_counties_response import CountiesPhpGetAvailableCountiesResponse

__all__ = ["CountiesPhpResource", "AsyncCountiesPhpResource"]


class CountiesPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CountiesPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return CountiesPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CountiesPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return CountiesPhpResourceWithStreamingResponse(self)

    def get_available_counties(
        self,
        *,
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CountiesPhpGetAvailableCountiesResponse:
        """Get available for les_engine calls.

        Please request that this functionality be
        turned on.

        Args:
          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/counties.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "session_id": session_id,
                        "state": state,
                    },
                    counties_php_get_available_counties_params.CountiesPhpGetAvailableCountiesParams,
                ),
            ),
            cast_to=CountiesPhpGetAvailableCountiesResponse,
        )


class AsyncCountiesPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCountiesPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncCountiesPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCountiesPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncCountiesPhpResourceWithStreamingResponse(self)

    async def get_available_counties(
        self,
        *,
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> CountiesPhpGetAvailableCountiesResponse:
        """Get available for les_engine calls.

        Please request that this functionality be
        turned on.

        Args:
          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/counties.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "session_id": session_id,
                        "state": state,
                    },
                    counties_php_get_available_counties_params.CountiesPhpGetAvailableCountiesParams,
                ),
            ),
            cast_to=CountiesPhpGetAvailableCountiesResponse,
        )


class CountiesPhpResourceWithRawResponse:
    def __init__(self, counties_php: CountiesPhpResource) -> None:
        self._counties_php = counties_php

        self.get_available_counties = to_raw_response_wrapper(
            counties_php.get_available_counties,
        )


class AsyncCountiesPhpResourceWithRawResponse:
    def __init__(self, counties_php: AsyncCountiesPhpResource) -> None:
        self._counties_php = counties_php

        self.get_available_counties = async_to_raw_response_wrapper(
            counties_php.get_available_counties,
        )


class CountiesPhpResourceWithStreamingResponse:
    def __init__(self, counties_php: CountiesPhpResource) -> None:
        self._counties_php = counties_php

        self.get_available_counties = to_streamed_response_wrapper(
            counties_php.get_available_counties,
        )


class AsyncCountiesPhpResourceWithStreamingResponse:
    def __init__(self, counties_php: AsyncCountiesPhpResource) -> None:
        self._counties_php = counties_php

        self.get_available_counties = async_to_streamed_response_wrapper(
            counties_php.get_available_counties,
        )
