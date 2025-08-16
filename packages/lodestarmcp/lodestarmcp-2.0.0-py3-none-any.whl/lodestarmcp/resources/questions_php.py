# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import questions_php_get_questions_params
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
from ..types.questions_php_get_questions_response import QuestionsPhpGetQuestionsResponse

__all__ = ["QuestionsPhpResource", "AsyncQuestionsPhpResource"]


class QuestionsPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> QuestionsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return QuestionsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> QuestionsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return QuestionsPhpResourceWithStreamingResponse(self)

    def get_questions(
        self,
        *,
        purpose: Literal["00", "11", "04"],
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionsPhpGetQuestionsResponse:
        """
        Retreive questions that should be asked for a specific calculation to get most
        acurate result

        Args:
          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/questions.php",
            body=maybe_transform(
                {
                    "purpose": purpose,
                    "session_id": session_id,
                    "state": state,
                },
                questions_php_get_questions_params.QuestionsPhpGetQuestionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionsPhpGetQuestionsResponse,
        )


class AsyncQuestionsPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncQuestionsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncQuestionsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncQuestionsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncQuestionsPhpResourceWithStreamingResponse(self)

    async def get_questions(
        self,
        *,
        purpose: Literal["00", "11", "04"],
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> QuestionsPhpGetQuestionsResponse:
        """
        Retreive questions that should be asked for a specific calculation to get most
        acurate result

        Args:
          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/questions.php",
            body=await async_maybe_transform(
                {
                    "purpose": purpose,
                    "session_id": session_id,
                    "state": state,
                },
                questions_php_get_questions_params.QuestionsPhpGetQuestionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=QuestionsPhpGetQuestionsResponse,
        )


class QuestionsPhpResourceWithRawResponse:
    def __init__(self, questions_php: QuestionsPhpResource) -> None:
        self._questions_php = questions_php

        self.get_questions = to_raw_response_wrapper(
            questions_php.get_questions,
        )


class AsyncQuestionsPhpResourceWithRawResponse:
    def __init__(self, questions_php: AsyncQuestionsPhpResource) -> None:
        self._questions_php = questions_php

        self.get_questions = async_to_raw_response_wrapper(
            questions_php.get_questions,
        )


class QuestionsPhpResourceWithStreamingResponse:
    def __init__(self, questions_php: QuestionsPhpResource) -> None:
        self._questions_php = questions_php

        self.get_questions = to_streamed_response_wrapper(
            questions_php.get_questions,
        )


class AsyncQuestionsPhpResourceWithStreamingResponse:
    def __init__(self, questions_php: AsyncQuestionsPhpResource) -> None:
        self._questions_php = questions_php

        self.get_questions = async_to_streamed_response_wrapper(
            questions_php.get_questions,
        )
