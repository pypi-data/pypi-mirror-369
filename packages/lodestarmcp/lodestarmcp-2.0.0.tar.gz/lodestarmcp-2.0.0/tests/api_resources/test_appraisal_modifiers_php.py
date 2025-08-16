# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import AppraisalModifiersPhpGetAvailableResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAppraisalModifiersPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available(self, client: Lodestarmcp) -> None:
        appraisal_modifiers_php = client.appraisal_modifiers_php.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available_with_all_params(self, client: Lodestarmcp) -> None:
        appraisal_modifiers_php = client.appraisal_modifiers_php.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
            loan_info_amort_type=0,
            loan_info_loan_type=0,
            loan_info_prop_type=0,
        )
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_available(self, client: Lodestarmcp) -> None:
        response = client.appraisal_modifiers_php.with_raw_response.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appraisal_modifiers_php = response.parse()
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_available(self, client: Lodestarmcp) -> None:
        with client.appraisal_modifiers_php.with_streaming_response.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appraisal_modifiers_php = response.parse()
            assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAppraisalModifiersPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available(self, async_client: AsyncLodestarmcp) -> None:
        appraisal_modifiers_php = await async_client.appraisal_modifiers_php.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available_with_all_params(self, async_client: AsyncLodestarmcp) -> None:
        appraisal_modifiers_php = await async_client.appraisal_modifiers_php.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
            loan_info_amort_type=0,
            loan_info_loan_type=0,
            loan_info_prop_type=0,
        )
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_available(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.appraisal_modifiers_php.with_raw_response.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        appraisal_modifiers_php = await response.parse()
        assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_available(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.appraisal_modifiers_php.with_streaming_response.get_available(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            appraisal_modifiers_php = await response.parse()
            assert_matches_type(AppraisalModifiersPhpGetAvailableResponse, appraisal_modifiers_php, path=["response"])

        assert cast(Any, response.is_closed) is True
