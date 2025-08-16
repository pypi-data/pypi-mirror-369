# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, Dict, List, Union, Iterable, cast
from datetime import date
from typing_extensions import Literal

import httpx

from ..types import closing_cost_calculations_php_calculate_params
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
from ..types.closing_cost_calculations_php_calculate_response import ClosingCostCalculationsPhpCalculateResponse

__all__ = ["ClosingCostCalculationsPhpResource", "AsyncClosingCostCalculationsPhpResource"]


class ClosingCostCalculationsPhpResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClosingCostCalculationsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return ClosingCostCalculationsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClosingCostCalculationsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return ClosingCostCalculationsPhpResourceWithStreamingResponse(self)

    def calculate(
        self,
        *,
        county: str,
        purpose: Literal["00", "11", "04"],
        search_type: Literal["CFPB", "Title"],
        session_id: str,
        state: str,
        township: str,
        address: str | NotGiven = NOT_GIVEN,
        agent_id: int | NotGiven = NOT_GIVEN,
        app_mods: Iterable[int] | NotGiven = NOT_GIVEN,
        client_id: int | NotGiven = NOT_GIVEN,
        close_date: Union[str, date] | NotGiven = NOT_GIVEN,
        doc_type: closing_cost_calculations_php_calculate_params.DocType | NotGiven = NOT_GIVEN,
        exdebt: float | NotGiven = NOT_GIVEN,
        filename: str | NotGiven = NOT_GIVEN,
        include_appraisal: int | NotGiven = NOT_GIVEN,
        include_full_policy_amount: int | NotGiven = NOT_GIVEN,
        include_payee_info: int | NotGiven = NOT_GIVEN,
        include_pdf: int | NotGiven = NOT_GIVEN,
        include_property_tax: int | NotGiven = NOT_GIVEN,
        include_section: int | NotGiven = NOT_GIVEN,
        include_seller_responsible: int | NotGiven = NOT_GIVEN,
        int_name: str | NotGiven = NOT_GIVEN,
        loan_amount: float | NotGiven = NOT_GIVEN,
        loan_info: LoanInfoParam | NotGiven = NOT_GIVEN,
        loanpol_level: Literal[1, 2] | NotGiven = NOT_GIVEN,
        owners_level: Literal[1, 2] | NotGiven = NOT_GIVEN,
        prior_insurance: float | NotGiven = NOT_GIVEN,
        prior_insurance_date: Union[str, date] | NotGiven = NOT_GIVEN,
        purchase_price: float | NotGiven = NOT_GIVEN,
        qst: Dict[str, str] | NotGiven = NOT_GIVEN,
        request_endos: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClosingCostCalculationsPhpCalculateResponse:
        """
        This method is used to calculate title agent fees, title premiums, and recording
        fees/taxes.

        There are two different types of optional parameters that can be passed to this
        method:

        - Calculation Parameters will modify how the fees will be calculated (i.e. Is
          the property a primary residence will lower the tax).
        - Output Parameters will modify what information is returned (.i.e. include_pdf
          will add a base64 encoded pdf the response).

        Make sure to click on the request body and response body schema to read about
        the property descriptions.

        All possible non-endorsement FeeNames can be found
        [here](https://www.lodestarss.com/API/Standard_Title_FeeNames.csv)

        All possible recording and tax types can be found
        [here:](https://www.lodestarss.com/API/Recording_Fee_And_Tax_Names.csv)

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          search_type:
              Controls what type of response data is needed Purpose Types:

              - `CFPB` - Returns tax, recording fees, title fees and title premiums.
              - `Title` - Title fees and title premiums only.

          session_id: The string returned from the `LOGIN /Login/login.php` method

          agent_id: # Optional Calculation Parameter

              Sub Agent office id that specifies which office for a title Title Agent/Escrow
              Agent to use. Very frequently agent_id of 1 should be used. Only used for
              Originator Setups. Values is pulled from the sub_agent end point
              sub_agent_office_id value.'

          app_mods: # Optional Calculation Parameter If Appraisal Calculations Requested

              Array of appraisal modifications that shoul be added to appraisal. List of
              possibile appraisal modifications can be retreived from appraisal_modifiers
              endpoint.

          client_id: # Optional Calculation Parameter

              Sub Agent id that specifies which Title Agent/Escrow Agent to use. Only used for
              Originator Setups. Values is pulled from the sub_agent end point sub_agent_id
              value.'

          doc_type: # Optional Calculation Parameter

              Contains which doucments need to be caluclated for the transaction. Document
              Types:

              - `deed` - Deed
              - `mort` - Mortgage/Deed Of Trust
              - `release` - Release of Real Estate Lien
              - `att` - Power Of Attorney
              - `assign` - Assignment
              - `sub` - Subordination
              - `mod` - Modification

          exdebt: # For Refinance Quotes Only

              # Optional Calculation Parameter

              Parameter that is used for some refinance calulcations. The Questions endpoint
              will define if this field is needed.

          filename: The unique file/loan name that the quote will be made for. This file name can be
              used for billing, tracking, and retrieval purposes.

          include_appraisal: ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL APPRAISAL CHARGE # Optional Output Parameter

              Will include the appraisal calculations. This also provides the advantage of
              having the appraisal fee include in the PDF output. \\** `1` - Will include the
              appraisal calculations.

          include_full_policy_amount: # Optional Output Parameter

              If full policy amount breakdowns are needed. This will mostly only be used by
              title agents. \\** `1` - Will return the breakdown

          include_payee_info: # Optional Output Parameter

              Will return payee info for all title_agent_fees, transfer_taxes, and
              recording_fees. \\** `1` - Will return the breakdown

          include_pdf: # Optional Output Parameter

              Will return PDF of the results mirrroring the LodeStar PDF output. \\** `1` - Will
              return the breakdown

          include_property_tax: ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL PROPERTY TAX CHARGE # Optional Output Parameter

              Will include the property tax calculations for the property instead of having to
              call the property_tax endpoint separately. This also provides the advantage of
              having the property taxes include in the PDF output. \\** `1` - Will include the
              property tax calculations.

          include_section: # Optional Output Parameter

              Will return what section in the LE/CD should the returned title agent and lender
              fees go into. \\** `1` - Will return the breakdown

          include_seller_responsible: # Optional Output Parameter

              Will add a property (seller_responsible) on the seller paid taxes that will be a
              boolean value indicating if the tax should be marked as seller responsible. \\**
              `1` - Will return additional property.

          int_name: A name to identify which integration is being used to make the request. Please
              ask LodeStar what this variable should be set to. If this is not properly set
              request might not be properly handled.

          loan_amount: Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed.

          loanpol_level: # Optional Calculation Parameter

              Loan Policy Level. For Title Agent use only. Document Types:

              - `1` - Standard Policy
              - `2` - Enhanced

          owners_level: # Optional Calculation Parameter

              Owners Policy Level. For Title Agent use only. Document Types:

              - `1` - Standard Policy
              - `2` - Enhanced

          prior_insurance: # For Refinance Quotes Only

              # Optional Calculation Parameter

              Optional input that is used for some refinance calulcations. The Questions
              endpoint will define if this field is needed.

          prior_insurance_date: This date is only useful for refinances when a reissue discount is being looked
              for. It represents the date of the previous insurance policy effective date
              (usually the previous mortgage policy close date)

          purchase_price: Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed.

          qst: # Optional Calculation Parameter

              Additional questions that can be answered. They are usually in the form of Q1
              => 1. However they can be more complex such as original_mort_date =>
              '01/10/2019'

          request_endos: # Optional Calculation Parameter

              Array of endorsements to get by ID. IDs can be retrieved from the endorsement
              endpoint. If endorsement endpoint is not available please contact support.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            ClosingCostCalculationsPhpCalculateResponse,
            self._post(
                "/closing_cost_calculations.php",
                body=maybe_transform(
                    {
                        "county": county,
                        "purpose": purpose,
                        "search_type": search_type,
                        "session_id": session_id,
                        "state": state,
                        "township": township,
                        "address": address,
                        "agent_id": agent_id,
                        "app_mods": app_mods,
                        "client_id": client_id,
                        "close_date": close_date,
                        "doc_type": doc_type,
                        "exdebt": exdebt,
                        "filename": filename,
                        "include_appraisal": include_appraisal,
                        "include_full_policy_amount": include_full_policy_amount,
                        "include_payee_info": include_payee_info,
                        "include_pdf": include_pdf,
                        "include_property_tax": include_property_tax,
                        "include_section": include_section,
                        "include_seller_responsible": include_seller_responsible,
                        "int_name": int_name,
                        "loan_amount": loan_amount,
                        "loan_info": loan_info,
                        "loanpol_level": loanpol_level,
                        "owners_level": owners_level,
                        "prior_insurance": prior_insurance,
                        "prior_insurance_date": prior_insurance_date,
                        "purchase_price": purchase_price,
                        "qst": qst,
                        "request_endos": request_endos,
                    },
                    closing_cost_calculations_php_calculate_params.ClosingCostCalculationsPhpCalculateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ClosingCostCalculationsPhpCalculateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class AsyncClosingCostCalculationsPhpResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClosingCostCalculationsPhpResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#accessing-raw-response-data-eg-headers
        """
        return AsyncClosingCostCalculationsPhpResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClosingCostCalculationsPhpResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/chasepkelly/lodestarmcp#with_streaming_response
        """
        return AsyncClosingCostCalculationsPhpResourceWithStreamingResponse(self)

    async def calculate(
        self,
        *,
        county: str,
        purpose: Literal["00", "11", "04"],
        search_type: Literal["CFPB", "Title"],
        session_id: str,
        state: str,
        township: str,
        address: str | NotGiven = NOT_GIVEN,
        agent_id: int | NotGiven = NOT_GIVEN,
        app_mods: Iterable[int] | NotGiven = NOT_GIVEN,
        client_id: int | NotGiven = NOT_GIVEN,
        close_date: Union[str, date] | NotGiven = NOT_GIVEN,
        doc_type: closing_cost_calculations_php_calculate_params.DocType | NotGiven = NOT_GIVEN,
        exdebt: float | NotGiven = NOT_GIVEN,
        filename: str | NotGiven = NOT_GIVEN,
        include_appraisal: int | NotGiven = NOT_GIVEN,
        include_full_policy_amount: int | NotGiven = NOT_GIVEN,
        include_payee_info: int | NotGiven = NOT_GIVEN,
        include_pdf: int | NotGiven = NOT_GIVEN,
        include_property_tax: int | NotGiven = NOT_GIVEN,
        include_section: int | NotGiven = NOT_GIVEN,
        include_seller_responsible: int | NotGiven = NOT_GIVEN,
        int_name: str | NotGiven = NOT_GIVEN,
        loan_amount: float | NotGiven = NOT_GIVEN,
        loan_info: LoanInfoParam | NotGiven = NOT_GIVEN,
        loanpol_level: Literal[1, 2] | NotGiven = NOT_GIVEN,
        owners_level: Literal[1, 2] | NotGiven = NOT_GIVEN,
        prior_insurance: float | NotGiven = NOT_GIVEN,
        prior_insurance_date: Union[str, date] | NotGiven = NOT_GIVEN,
        purchase_price: float | NotGiven = NOT_GIVEN,
        qst: Dict[str, str] | NotGiven = NOT_GIVEN,
        request_endos: List[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ClosingCostCalculationsPhpCalculateResponse:
        """
        This method is used to calculate title agent fees, title premiums, and recording
        fees/taxes.

        There are two different types of optional parameters that can be passed to this
        method:

        - Calculation Parameters will modify how the fees will be calculated (i.e. Is
          the property a primary residence will lower the tax).
        - Output Parameters will modify what information is returned (.i.e. include_pdf
          will add a base64 encoded pdf the response).

        Make sure to click on the request body and response body schema to read about
        the property descriptions.

        All possible non-endorsement FeeNames can be found
        [here](https://www.lodestarss.com/API/Standard_Title_FeeNames.csv)

        All possible recording and tax types can be found
        [here:](https://www.lodestarss.com/API/Recording_Fee_And_Tax_Names.csv)

        Args:
          county: County name. If the LodeStar County endpoint was not used and the county is
              supplied from the users own list LodeStar will try to use fuzzy logic to match
              similar names (i.e. Saint Mary's vs St. Marys). Do not include the word County
              (i.e. Saint Marys County vs Saint Marys)

          purpose: If a purpose has a leading zero it is required. There can be more options then
              the ones listed below. Please contact us if you require a different option
              Purpose Types:

              - `00` - Refinance
              - `04` - Refinance (Reissue)
              - `11` - Purchase

          search_type:
              Controls what type of response data is needed Purpose Types:

              - `CFPB` - Returns tax, recording fees, title fees and title premiums.
              - `Title` - Title fees and title premiums only.

          session_id: The string returned from the `LOGIN /Login/login.php` method

          agent_id: # Optional Calculation Parameter

              Sub Agent office id that specifies which office for a title Title Agent/Escrow
              Agent to use. Very frequently agent_id of 1 should be used. Only used for
              Originator Setups. Values is pulled from the sub_agent end point
              sub_agent_office_id value.'

          app_mods: # Optional Calculation Parameter If Appraisal Calculations Requested

              Array of appraisal modifications that shoul be added to appraisal. List of
              possibile appraisal modifications can be retreived from appraisal_modifiers
              endpoint.

          client_id: # Optional Calculation Parameter

              Sub Agent id that specifies which Title Agent/Escrow Agent to use. Only used for
              Originator Setups. Values is pulled from the sub_agent end point sub_agent_id
              value.'

          doc_type: # Optional Calculation Parameter

              Contains which doucments need to be caluclated for the transaction. Document
              Types:

              - `deed` - Deed
              - `mort` - Mortgage/Deed Of Trust
              - `release` - Release of Real Estate Lien
              - `att` - Power Of Attorney
              - `assign` - Assignment
              - `sub` - Subordination
              - `mod` - Modification

          exdebt: # For Refinance Quotes Only

              # Optional Calculation Parameter

              Parameter that is used for some refinance calulcations. The Questions endpoint
              will define if this field is needed.

          filename: The unique file/loan name that the quote will be made for. This file name can be
              used for billing, tracking, and retrieval purposes.

          include_appraisal: ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL APPRAISAL CHARGE # Optional Output Parameter

              Will include the appraisal calculations. This also provides the advantage of
              having the appraisal fee include in the PDF output. \\** `1` - Will include the
              appraisal calculations.

          include_full_policy_amount: # Optional Output Parameter

              If full policy amount breakdowns are needed. This will mostly only be used by
              title agents. \\** `1` - Will return the breakdown

          include_payee_info: # Optional Output Parameter

              Will return payee info for all title_agent_fees, transfer_taxes, and
              recording_fees. \\** `1` - Will return the breakdown

          include_pdf: # Optional Output Parameter

              Will return PDF of the results mirrroring the LodeStar PDF output. \\** `1` - Will
              return the breakdown

          include_property_tax: ##### WARNING REQUESTING THIS PROPERTY WILL INCUR AN ADDITIONAL PROPERTY TAX CHARGE # Optional Output Parameter

              Will include the property tax calculations for the property instead of having to
              call the property_tax endpoint separately. This also provides the advantage of
              having the property taxes include in the PDF output. \\** `1` - Will include the
              property tax calculations.

          include_section: # Optional Output Parameter

              Will return what section in the LE/CD should the returned title agent and lender
              fees go into. \\** `1` - Will return the breakdown

          include_seller_responsible: # Optional Output Parameter

              Will add a property (seller_responsible) on the seller paid taxes that will be a
              boolean value indicating if the tax should be marked as seller responsible. \\**
              `1` - Will return additional property.

          int_name: A name to identify which integration is being used to make the request. Please
              ask LodeStar what this variable should be set to. If this is not properly set
              request might not be properly handled.

          loan_amount: Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed.

          loanpol_level: # Optional Calculation Parameter

              Loan Policy Level. For Title Agent use only. Document Types:

              - `1` - Standard Policy
              - `2` - Enhanced

          owners_level: # Optional Calculation Parameter

              Owners Policy Level. For Title Agent use only. Document Types:

              - `1` - Standard Policy
              - `2` - Enhanced

          prior_insurance: # For Refinance Quotes Only

              # Optional Calculation Parameter

              Optional input that is used for some refinance calulcations. The Questions
              endpoint will define if this field is needed.

          prior_insurance_date: This date is only useful for refinances when a reissue discount is being looked
              for. It represents the date of the previous insurance policy effective date
              (usually the previous mortgage policy close date)

          purchase_price: Can also be in currency format (i.e. 200,000). Defaults to 0 if not passed.

          qst: # Optional Calculation Parameter

              Additional questions that can be answered. They are usually in the form of Q1
              => 1. However they can be more complex such as original_mort_date =>
              '01/10/2019'

          request_endos: # Optional Calculation Parameter

              Array of endorsements to get by ID. IDs can be retrieved from the endorsement
              endpoint. If endorsement endpoint is not available please contact support.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return cast(
            ClosingCostCalculationsPhpCalculateResponse,
            await self._post(
                "/closing_cost_calculations.php",
                body=await async_maybe_transform(
                    {
                        "county": county,
                        "purpose": purpose,
                        "search_type": search_type,
                        "session_id": session_id,
                        "state": state,
                        "township": township,
                        "address": address,
                        "agent_id": agent_id,
                        "app_mods": app_mods,
                        "client_id": client_id,
                        "close_date": close_date,
                        "doc_type": doc_type,
                        "exdebt": exdebt,
                        "filename": filename,
                        "include_appraisal": include_appraisal,
                        "include_full_policy_amount": include_full_policy_amount,
                        "include_payee_info": include_payee_info,
                        "include_pdf": include_pdf,
                        "include_property_tax": include_property_tax,
                        "include_section": include_section,
                        "include_seller_responsible": include_seller_responsible,
                        "int_name": int_name,
                        "loan_amount": loan_amount,
                        "loan_info": loan_info,
                        "loanpol_level": loanpol_level,
                        "owners_level": owners_level,
                        "prior_insurance": prior_insurance,
                        "prior_insurance_date": prior_insurance_date,
                        "purchase_price": purchase_price,
                        "qst": qst,
                        "request_endos": request_endos,
                    },
                    closing_cost_calculations_php_calculate_params.ClosingCostCalculationsPhpCalculateParams,
                ),
                options=make_request_options(
                    extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
                ),
                cast_to=cast(
                    Any, ClosingCostCalculationsPhpCalculateResponse
                ),  # Union types cannot be passed in as arguments in the type system
            ),
        )


class ClosingCostCalculationsPhpResourceWithRawResponse:
    def __init__(self, closing_cost_calculations_php: ClosingCostCalculationsPhpResource) -> None:
        self._closing_cost_calculations_php = closing_cost_calculations_php

        self.calculate = to_raw_response_wrapper(
            closing_cost_calculations_php.calculate,
        )


class AsyncClosingCostCalculationsPhpResourceWithRawResponse:
    def __init__(self, closing_cost_calculations_php: AsyncClosingCostCalculationsPhpResource) -> None:
        self._closing_cost_calculations_php = closing_cost_calculations_php

        self.calculate = async_to_raw_response_wrapper(
            closing_cost_calculations_php.calculate,
        )


class ClosingCostCalculationsPhpResourceWithStreamingResponse:
    def __init__(self, closing_cost_calculations_php: ClosingCostCalculationsPhpResource) -> None:
        self._closing_cost_calculations_php = closing_cost_calculations_php

        self.calculate = to_streamed_response_wrapper(
            closing_cost_calculations_php.calculate,
        )


class AsyncClosingCostCalculationsPhpResourceWithStreamingResponse:
    def __init__(self, closing_cost_calculations_php: AsyncClosingCostCalculationsPhpResource) -> None:
        self._closing_cost_calculations_php = closing_cost_calculations_php

        self.calculate = async_to_streamed_response_wrapper(
            closing_cost_calculations_php.calculate,
        )
