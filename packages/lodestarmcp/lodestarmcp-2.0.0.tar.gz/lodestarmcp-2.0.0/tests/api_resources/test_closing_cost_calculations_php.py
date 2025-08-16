# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import (
    ClosingCostCalculationsPhpCalculateResponse,
)
from lodestarmcp._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClosingCostCalculationsPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_calculate(self, client: Lodestarmcp) -> None:
        closing_cost_calculations_php = client.closing_cost_calculations_php.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        )
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_calculate_with_all_params(self, client: Lodestarmcp) -> None:
        closing_cost_calculations_php = client.closing_cost_calculations_php.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
            address="110 Jefferson St. Apt 2",
            agent_id=0,
            app_mods=[3, 7],
            client_id=0,
            close_date=parse_date("2022-11-04"),
            doc_type={
                "assign": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "att": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "deed": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "mod": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "mort": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "release": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "sub": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
            },
            exdebt=0,
            filename="filename",
            include_appraisal=0,
            include_full_policy_amount=0,
            include_payee_info=0,
            include_pdf=0,
            include_property_tax=0,
            include_section=0,
            include_seller_responsible=0,
            int_name="int_name",
            loan_amount=200000,
            loan_info={
                "amort_type": 1,
                "is_federal_credit_union": 1,
                "is_first_time_home_buyer": 1,
                "is_same_borrwers_as_previous": 1,
                "is_same_lender_as_previous": 1,
                "loan_type": 1,
                "number_of_families": 3,
                "prop_purpose": 1,
                "prop_type": 1,
                "prop_usage": 1,
            },
            loanpol_level=1,
            owners_level=1,
            prior_insurance=0,
            prior_insurance_date=parse_date("2020-05-02"),
            purchase_price=300000,
            qst={"foo": "string"},
            request_endos=["string"],
        )
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_calculate(self, client: Lodestarmcp) -> None:
        response = client.closing_cost_calculations_php.with_raw_response.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        closing_cost_calculations_php = response.parse()
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_calculate(self, client: Lodestarmcp) -> None:
        with client.closing_cost_calculations_php.with_streaming_response.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            closing_cost_calculations_php = response.parse()
            assert_matches_type(
                ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
            )

        assert cast(Any, response.is_closed) is True


class TestAsyncClosingCostCalculationsPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_calculate(self, async_client: AsyncLodestarmcp) -> None:
        closing_cost_calculations_php = await async_client.closing_cost_calculations_php.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        )
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_calculate_with_all_params(self, async_client: AsyncLodestarmcp) -> None:
        closing_cost_calculations_php = await async_client.closing_cost_calculations_php.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
            address="110 Jefferson St. Apt 2",
            agent_id=0,
            app_mods=[3, 7],
            client_id=0,
            close_date=parse_date("2022-11-04"),
            doc_type={
                "assign": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "att": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "deed": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "mod": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "mort": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "release": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
                "sub": {
                    "num_count": 1,
                    "page_count": 25,
                    "num_grantees": 1,
                    "num_grantors": 1,
                    "num_names": 1,
                    "num_sigs": 1,
                },
            },
            exdebt=0,
            filename="filename",
            include_appraisal=0,
            include_full_policy_amount=0,
            include_payee_info=0,
            include_pdf=0,
            include_property_tax=0,
            include_section=0,
            include_seller_responsible=0,
            int_name="int_name",
            loan_amount=200000,
            loan_info={
                "amort_type": 1,
                "is_federal_credit_union": 1,
                "is_first_time_home_buyer": 1,
                "is_same_borrwers_as_previous": 1,
                "is_same_lender_as_previous": 1,
                "loan_type": 1,
                "number_of_families": 3,
                "prop_purpose": 1,
                "prop_type": 1,
                "prop_usage": 1,
            },
            loanpol_level=1,
            owners_level=1,
            prior_insurance=0,
            prior_insurance_date=parse_date("2020-05-02"),
            purchase_price=300000,
            qst={"foo": "string"},
            request_endos=["string"],
        )
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_calculate(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.closing_cost_calculations_php.with_raw_response.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        closing_cost_calculations_php = await response.parse()
        assert_matches_type(
            ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
        )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_calculate(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.closing_cost_calculations_php.with_streaming_response.calculate(
            county="Hudson",
            purpose="00",
            search_type="CFPB",
            session_id="session_id",
            state="NJ",
            township="Hoboken",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            closing_cost_calculations_php = await response.parse()
            assert_matches_type(
                ClosingCostCalculationsPhpCalculateResponse, closing_cost_calculations_php, path=["response"]
            )

        assert cast(Any, response.is_closed) is True
