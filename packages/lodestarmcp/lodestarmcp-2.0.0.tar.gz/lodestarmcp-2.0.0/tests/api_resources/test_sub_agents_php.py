# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import SubAgentsPhpGetAvailableSubAgentsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSubAgentsPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available_sub_agents(self, client: Lodestarmcp) -> None:
        sub_agents_php = client.sub_agents_php.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available_sub_agents_with_all_params(self, client: Lodestarmcp) -> None:
        sub_agents_php = client.sub_agents_php.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
            address="address",
            get_contact_info=0,
            township="township",
        )
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_available_sub_agents(self, client: Lodestarmcp) -> None:
        response = client.sub_agents_php.with_raw_response.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sub_agents_php = response.parse()
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_available_sub_agents(self, client: Lodestarmcp) -> None:
        with client.sub_agents_php.with_streaming_response.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sub_agents_php = response.parse()
            assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSubAgentsPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available_sub_agents(self, async_client: AsyncLodestarmcp) -> None:
        sub_agents_php = await async_client.sub_agents_php.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available_sub_agents_with_all_params(self, async_client: AsyncLodestarmcp) -> None:
        sub_agents_php = await async_client.sub_agents_php.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
            address="address",
            get_contact_info=0,
            township="township",
        )
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_available_sub_agents(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.sub_agents_php.with_raw_response.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        sub_agents_php = await response.parse()
        assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_available_sub_agents(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.sub_agents_php.with_streaming_response.get_available_sub_agents(
            county="county",
            purpose="purpose",
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            sub_agents_php = await response.parse()
            assert_matches_type(SubAgentsPhpGetAvailableSubAgentsResponse, sub_agents_php, path=["response"])

        assert cast(Any, response.is_closed) is True
