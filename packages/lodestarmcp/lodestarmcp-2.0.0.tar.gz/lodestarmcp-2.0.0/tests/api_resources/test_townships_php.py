# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import TownshipsPhpGetAvailableTownshipsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTownshipsPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available_townships(self, client: Lodestarmcp) -> None:
        townships_php = client.townships_php.get_available_townships(
            county="county",
            session_id="session_id",
        )
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_available_townships_with_all_params(self, client: Lodestarmcp) -> None:
        townships_php = client.townships_php.get_available_townships(
            county="county",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_available_townships(self, client: Lodestarmcp) -> None:
        response = client.townships_php.with_raw_response.get_available_townships(
            county="county",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        townships_php = response.parse()
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_available_townships(self, client: Lodestarmcp) -> None:
        with client.townships_php.with_streaming_response.get_available_townships(
            county="county",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            townships_php = response.parse()
            assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTownshipsPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available_townships(self, async_client: AsyncLodestarmcp) -> None:
        townships_php = await async_client.townships_php.get_available_townships(
            county="county",
            session_id="session_id",
        )
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_available_townships_with_all_params(self, async_client: AsyncLodestarmcp) -> None:
        townships_php = await async_client.townships_php.get_available_townships(
            county="county",
            session_id="session_id",
            state="state",
        )
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_available_townships(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.townships_php.with_raw_response.get_available_townships(
            county="county",
            session_id="session_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        townships_php = await response.parse()
        assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_available_townships(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.townships_php.with_streaming_response.get_available_townships(
            county="county",
            session_id="session_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            townships_php = await response.parse()
            assert_matches_type(TownshipsPhpGetAvailableTownshipsResponse, townships_php, path=["response"])

        assert cast(Any, response.is_closed) is True
