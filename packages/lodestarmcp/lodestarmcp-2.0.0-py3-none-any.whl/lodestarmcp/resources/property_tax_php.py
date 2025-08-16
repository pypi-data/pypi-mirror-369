# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import date

import httpx

from ..types import property_tax_php_retrieve_params
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
from ..types.property_tax_php_retrieve_response import PropertyTaxPhpRetrieveResponse

__all__ = ["PropertyTaxPhpResource", "AsyncPropertyTaxPhpResource"]


class PropertyTaxPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PropertyTaxPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return PropertyTaxPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PropertyTaxPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return PropertyTaxPhpResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        address: str,
        city: str,
        close_date: Union[str, date],
        county: str,
        file_name: str,
        purchase_price: float,
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PropertyTaxPhpRetrieveResponse:
        """Get available property tax.

        At times the property tax might not be on file. Also
        note that all returned data is an estimate. Please request that this
        functionality be turned on.

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purchase_price: The purchase price or market value of the property is required for the
              calculation of the estiamted property taxes if no property tax record can be
              found.

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/property_tax.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "address": address,
                        "city": city,
                        "close_date": close_date,
                        "county": county,
                        "file_name": file_name,
                        "purchase_price": purchase_price,
                        "session_id": session_id,
                        "state": state,
                    },
                    property_tax_php_retrieve_params.PropertyTaxPhpRetrieveParams,
                ),
            ),
            cast_to=PropertyTaxPhpRetrieveResponse,
        )


class AsyncPropertyTaxPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPropertyTaxPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncPropertyTaxPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPropertyTaxPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncPropertyTaxPhpResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        address: str,
        city: str,
        close_date: Union[str, date],
        county: str,
        file_name: str,
        purchase_price: float,
        session_id: str,
        state: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> PropertyTaxPhpRetrieveResponse:
        """Get available property tax.

        At times the property tax might not be on file. Also
        note that all returned data is an estimate. Please request that this
        functionality be turned on.

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purchase_price: The purchase price or market value of the property is required for the
              calculation of the estiamted property taxes if no property tax record can be
              found.

          session_id: The string returned from the `LOGIN /Login/login.php` method

          state: 2 letter state abbreviation

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/property_tax.php",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "address": address,
                        "city": city,
                        "close_date": close_date,
                        "county": county,
                        "file_name": file_name,
                        "purchase_price": purchase_price,
                        "session_id": session_id,
                        "state": state,
                    },
                    property_tax_php_retrieve_params.PropertyTaxPhpRetrieveParams,
                ),
            ),
            cast_to=PropertyTaxPhpRetrieveResponse,
        )


class PropertyTaxPhpResourceWithRawResponse:
    def __init__(self, property_tax_php: PropertyTaxPhpResource) -> None:
        self._property_tax_php = property_tax_php

        self.retrieve = to_raw_response_wrapper(
            property_tax_php.retrieve,
        )


class AsyncPropertyTaxPhpResourceWithRawResponse:
    def __init__(self, property_tax_php: AsyncPropertyTaxPhpResource) -> None:
        self._property_tax_php = property_tax_php

        self.retrieve = async_to_raw_response_wrapper(
            property_tax_php.retrieve,
        )


class PropertyTaxPhpResourceWithStreamingResponse:
    def __init__(self, property_tax_php: PropertyTaxPhpResource) -> None:
        self._property_tax_php = property_tax_php

        self.retrieve = to_streamed_response_wrapper(
            property_tax_php.retrieve,
        )


class AsyncPropertyTaxPhpResourceWithStreamingResponse:
    def __init__(self, property_tax_php: AsyncPropertyTaxPhpResource) -> None:
        self._property_tax_php = property_tax_php

        self.retrieve = async_to_streamed_response_wrapper(
            property_tax_php.retrieve,
        )
