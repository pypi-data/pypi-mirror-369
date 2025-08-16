# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import login_authenticate_params
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
from ..types.login_authenticate_response import LoginAuthenticateResponse

__all__ = ["LoginResource", "AsyncLoginResource"]


class LoginResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LoginResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return LoginResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LoginResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return LoginResourceWithStreamingResponse(self)

    def authenticate(
        self,
        *,
        password: str,
        username: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LoginAuthenticateResponse:
        """
        Logs user into LodeStar System

        Args:
          password: Password specific to the user

          username: Username to log into the system. Usually an email address

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/Login/login.php",
            body=maybe_transform(
                {
                    "password": password,
                    "username": username,
                },
                login_authenticate_params.LoginAuthenticateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginAuthenticateResponse,
        )


class AsyncLoginResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLoginResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncLoginResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLoginResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncLoginResourceWithStreamingResponse(self)

    async def authenticate(
        self,
        *,
        password: str,
        username: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LoginAuthenticateResponse:
        """
        Logs user into LodeStar System

        Args:
          password: Password specific to the user

          username: Username to log into the system. Usually an email address

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/Login/login.php",
            body=await async_maybe_transform(
                {
                    "password": password,
                    "username": username,
                },
                login_authenticate_params.LoginAuthenticateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginAuthenticateResponse,
        )


class LoginResourceWithRawResponse:
    def __init__(self, login: LoginResource) -> None:
        self._login = login

        self.authenticate = to_raw_response_wrapper(
            login.authenticate,
        )


class AsyncLoginResourceWithRawResponse:
    def __init__(self, login: AsyncLoginResource) -> None:
        self._login = login

        self.authenticate = async_to_raw_response_wrapper(
            login.authenticate,
        )


class LoginResourceWithStreamingResponse:
    def __init__(self, login: LoginResource) -> None:
        self._login = login

        self.authenticate = to_streamed_response_wrapper(
            login.authenticate,
        )


class AsyncLoginResourceWithStreamingResponse:
    def __init__(self, login: AsyncLoginResource) -> None:
        self._login = login

        self.authenticate = async_to_streamed_response_wrapper(
            login.authenticate,
        )
