# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import appraisal_modifiers_php_get_available_params
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
from ..types.appraisal_modifiers_php_get_available_response import AppraisalModifiersPhpGetAvailableResponse

__all__ = ["AppraisalModifiersPhpResource", "AsyncAppraisalModifiersPhpResource"]


class AppraisalModifiersPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AppraisalModifiersPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AppraisalModifiersPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AppraisalModifiersPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AppraisalModifiersPhpResourceWithStreamingResponse(self)

    def get_available(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        loan_info_amort_type: int | NotGiven = NOT_GIVEN,
        loan_info_loan_type: int | NotGiven = NOT_GIVEN,
        loan_info_prop_type: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AppraisalModifiersPhpGetAvailableResponse:
        """Get available appraisal modifiers.

        This method is only required if the appraisal
        fees are going to be calcualted.

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

          loan_info_amort_type: Optional property that describes what type of amortization scheudule is used for
              the loan . Amort Types:

              - `1` - Fixed Rate
              - `2` - Adjustable Rate

          loan_info_loan_type: Optional property that describes what type of loan program is being used. Loan
              Types:

              - `1` - Conventional
              - `2` - FHA
              - `3` - VA
              - `4` - USDA

          loan_info_prop_type: Optional property that describes what type of subject property is being run.
              Prop Types:

              - `1` - Single Family
              - `2` - Multi Family
              - `3` - Condo
              - `4` - Coop
              - `5` - PUD
              - `6` - Manufactured
              - `7` - Land example: 1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/appraisal_modifiers.php",
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
                        "loan_info_amort_type": loan_info_amort_type,
                        "loan_info_loan_type": loan_info_loan_type,
                        "loan_info_prop_type": loan_info_prop_type,
                    },
                    appraisal_modifiers_php_get_available_params.AppraisalModifiersPhpGetAvailableParams,
                ),
            ),
            cast_to=AppraisalModifiersPhpGetAvailableResponse,
        )


class AsyncAppraisalModifiersPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAppraisalModifiersPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncAppraisalModifiersPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAppraisalModifiersPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncAppraisalModifiersPhpResourceWithStreamingResponse(self)

    async def get_available(
        self,
        *,
        county: str,
        purpose: str,
        session_id: str,
        state: str,
        loan_info_amort_type: int | NotGiven = NOT_GIVEN,
        loan_info_loan_type: int | NotGiven = NOT_GIVEN,
        loan_info_prop_type: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AppraisalModifiersPhpGetAvailableResponse:
        """Get available appraisal modifiers.

        This method is only required if the appraisal
        fees are going to be calcualted.

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

          loan_info_amort_type: Optional property that describes what type of amortization scheudule is used for
              the loan . Amort Types:

              - `1` - Fixed Rate
              - `2` - Adjustable Rate

          loan_info_loan_type: Optional property that describes what type of loan program is being used. Loan
              Types:

              - `1` - Conventional
              - `2` - FHA
              - `3` - VA
              - `4` - USDA

          loan_info_prop_type: Optional property that describes what type of subject property is being run.
              Prop Types:

              - `1` - Single Family
              - `2` - Multi Family
              - `3` - Condo
              - `4` - Coop
              - `5` - PUD
              - `6` - Manufactured
              - `7` - Land example: 1

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/appraisal_modifiers.php",
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
                        "loan_info_amort_type": loan_info_amort_type,
                        "loan_info_loan_type": loan_info_loan_type,
                        "loan_info_prop_type": loan_info_prop_type,
                    },
                    appraisal_modifiers_php_get_available_params.AppraisalModifiersPhpGetAvailableParams,
                ),
            ),
            cast_to=AppraisalModifiersPhpGetAvailableResponse,
        )


class AppraisalModifiersPhpResourceWithRawResponse:
    def __init__(self, appraisal_modifiers_php: AppraisalModifiersPhpResource) -> None:
        self._appraisal_modifiers_php = appraisal_modifiers_php

        self.get_available = to_raw_response_wrapper(
            appraisal_modifiers_php.get_available,
        )


class AsyncAppraisalModifiersPhpResourceWithRawResponse:
    def __init__(self, appraisal_modifiers_php: AsyncAppraisalModifiersPhpResource) -> None:
        self._appraisal_modifiers_php = appraisal_modifiers_php

        self.get_available = async_to_raw_response_wrapper(
            appraisal_modifiers_php.get_available,
        )


class AppraisalModifiersPhpResourceWithStreamingResponse:
    def __init__(self, appraisal_modifiers_php: AppraisalModifiersPhpResource) -> None:
        self._appraisal_modifiers_php = appraisal_modifiers_php

        self.get_available = to_streamed_response_wrapper(
            appraisal_modifiers_php.get_available,
        )


class AsyncAppraisalModifiersPhpResourceWithStreamingResponse:
    def __init__(self, appraisal_modifiers_php: AsyncAppraisalModifiersPhpResource) -> None:
        self._appraisal_modifiers_php = appraisal_modifiers_php

        self.get_available = async_to_streamed_response_wrapper(
            appraisal_modifiers_php.get_available,
        )
