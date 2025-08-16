# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import geocode_check_php_check_params
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
from ..types.geocode_check_php_check_response import GeocodeCheckPhpCheckResponse

__all__ = ["GeocodeCheckPhpResource", "AsyncGeocodeCheckPhpResource"]


class GeocodeCheckPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GeocodeCheckPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return GeocodeCheckPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GeocodeCheckPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return GeocodeCheckPhpResourceWithStreamingResponse(self)

    def check(
        self,
        *,
        address: str,
        county: str,
        session_id: str,
        state: str,
        township: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeCheckPhpCheckResponse:
        """
        In PA (and some other states) there are townships within municipalities that
        have different taxes. For example in Media there is Upper Providence township
        that has additional transfer taxes that Media does not. However sometimes the
        addresses for these inner townships are not passed as the inner township but
        instead are passed as the larger municipality. For example 229 Summit Rd Media
        PA is actually in Upper Providence township but its mailing address is still in
        Media.

        The following inputs are required: session_id: same session_id that is required
        for all other endpoints

        state: 2 letter state abbrev that the property is located in(example PA)

        county: County name that the property is located in (example Delaware)

        township: The township or city that is the property is located in. Passing the
        township or the city should work but you should be passing what you expect to be
        the correct name. (example Upper Providence)address: The address of the property
        (229 Summit Rd)

        Successful response will include the suggested county (sometimes city is in
        multiple counties and the wrong county is passed), the suggested township that
        should be used (can be the city/township name passed to the request), and
        possible township options for the county/address.

        Also "All Townships" and "All other Townships" options will never be returned so
        as not to add confusion.

        The workflow for an interation would be checking if the township/city being
        requested is correct/a "relevant" data point for this search. If the
        township/city is incorrect the correct value will be returned in the
        suggested_township parameter. If the township/city is correct the
        suggested_township will just mirror back the same value as passed.
        township_options will include all possible options for the county that matter so
        as not to limit a user in case we are wrong with the matching.

        Example
        Request:https://www.lodestarss.com/Live/State_Financial-MB/geocode_check.php?session_id=hid29kxxxxm2v2h7f2ggn9&state=PA&county=Delaware&township=Media&address=229
        Summit Rd

        Example Response:
        {"status":1,"suggested_county":"Delaware","suggested_township":"Upper
        Providence","township_options":["Radnor","Upper Darby","Upper Providence"]}

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/geocode_check.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "address": address,
                        "county": county,
                        "session_id": session_id,
                        "state": state,
                        "township": township,
                    },
                    geocode_check_php_check_params.GeocodeCheckPhpCheckParams,
                ),
            ),
            cast_to=GeocodeCheckPhpCheckResponse,
        )


class AsyncGeocodeCheckPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGeocodeCheckPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncGeocodeCheckPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGeocodeCheckPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncGeocodeCheckPhpResourceWithStreamingResponse(self)

    async def check(
        self,
        *,
        address: str,
        county: str,
        session_id: str,
        state: str,
        township: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> GeocodeCheckPhpCheckResponse:
        """
        In PA (and some other states) there are townships within municipalities that
        have different taxes. For example in Media there is Upper Providence township
        that has additional transfer taxes that Media does not. However sometimes the
        addresses for these inner townships are not passed as the inner township but
        instead are passed as the larger municipality. For example 229 Summit Rd Media
        PA is actually in Upper Providence township but its mailing address is still in
        Media.

        The following inputs are required: session_id: same session_id that is required
        for all other endpoints

        state: 2 letter state abbrev that the property is located in(example PA)

        county: County name that the property is located in (example Delaware)

        township: The township or city that is the property is located in. Passing the
        township or the city should work but you should be passing what you expect to be
        the correct name. (example Upper Providence)address: The address of the property
        (229 Summit Rd)

        Successful response will include the suggested county (sometimes city is in
        multiple counties and the wrong county is passed), the suggested township that
        should be used (can be the city/township name passed to the request), and
        possible township options for the county/address.

        Also "All Townships" and "All other Townships" options will never be returned so
        as not to add confusion.

        The workflow for an interation would be checking if the township/city being
        requested is correct/a "relevant" data point for this search. If the
        township/city is incorrect the correct value will be returned in the
        suggested_township parameter. If the township/city is correct the
        suggested_township will just mirror back the same value as passed.
        township_options will include all possible options for the county that matter so
        as not to limit a user in case we are wrong with the matching.

        Example
        Request:https://www.lodestarss.com/Live/State_Financial-MB/geocode_check.php?session_id=hid29kxxxxm2v2h7f2ggn9&state=PA&county=Delaware&township=Media&address=229
        Summit Rd

        Example Response:
        {"status":1,"suggested_county":"Delaware","suggested_township":"Upper
        Providence","township_options":["Radnor","Upper Darby","Upper Providence"]}

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/geocode_check.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "address": address,
                        "county": county,
                        "session_id": session_id,
                        "state": state,
                        "township": township,
                    },
                    geocode_check_php_check_params.GeocodeCheckPhpCheckParams,
                ),
            ),
            cast_to=GeocodeCheckPhpCheckResponse,
        )


class GeocodeCheckPhpResourceWithRawResponse:
    def __init__(self, geocode_check_php: GeocodeCheckPhpResource) -> None:
        self._geocode_check_php = geocode_check_php

        self.check = to_raw_response_wrapper(
            geocode_check_php.check,
        )


class AsyncGeocodeCheckPhpResourceWithRawResponse:
    def __init__(self, geocode_check_php: AsyncGeocodeCheckPhpResource) -> None:
        self._geocode_check_php = geocode_check_php

        self.check = async_to_raw_response_wrapper(
            geocode_check_php.check,
        )


class GeocodeCheckPhpResourceWithStreamingResponse:
    def __init__(self, geocode_check_php: GeocodeCheckPhpResource) -> None:
        self._geocode_check_php = geocode_check_php

        self.check = to_streamed_response_wrapper(
            geocode_check_php.check,
        )


class AsyncGeocodeCheckPhpResourceWithStreamingResponse:
    def __init__(self, geocode_check_php: AsyncGeocodeCheckPhpResource) -> None:
        self._geocode_check_php = geocode_check_php

        self.check = async_to_streamed_response_wrapper(
            geocode_check_php.check,
        )
