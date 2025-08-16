# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import EndorsementsPhpListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEndorsementsPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Lodestarmcp) -> None:
        endorsements_php = client.endorsements_php.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Lodestarmcp) -> None:
        endorsements_php = client.endorsements_php.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
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
            sub_agent_id=0,
            sub_agent_office_id=0,
        )
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Lodestarmcp) -> None:
        response = client.endorsements_php.with_raw_response.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endorsements_php = response.parse()
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Lodestarmcp) -> None:
        with client.endorsements_php.with_streaming_response.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endorsements_php = response.parse()
            assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEndorsementsPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLodestarmcp) -> None:
        endorsements_php = await async_client.endorsements_php.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLodestarmcp) -> None:
        endorsements_php = await async_client.endorsements_php.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
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
            sub_agent_id=0,
            sub_agent_office_id=0,
        )
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.endorsements_php.with_raw_response.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        endorsements_php = await response.parse()
        assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.endorsements_php.with_streaming_response.list(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            endorsements_php = await response.parse()
            assert_matches_type(EndorsementsPhpListResponse, endorsements_php, path=["response"])

        assert cast(Any, response.is_closed) is True
