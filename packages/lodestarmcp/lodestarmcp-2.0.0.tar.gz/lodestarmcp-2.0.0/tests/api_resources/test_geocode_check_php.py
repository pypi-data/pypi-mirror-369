# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import GeocodeCheckPhpCheckResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGeocodeCheckPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check(self, client: Lodestarmcp) -> None:
        geocode_check_php = client.geocode_check_php.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        )
        assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check(self, client: Lodestarmcp) -> None:
        response = client.geocode_check_php.with_raw_response.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode_check_php = response.parse()
        assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check(self, client: Lodestarmcp) -> None:
        with client.geocode_check_php.with_streaming_response.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode_check_php = response.parse()
            assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGeocodeCheckPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check(self, async_client: AsyncLodestarmcp) -> None:
        geocode_check_php = await async_client.geocode_check_php.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        )
        assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.geocode_check_php.with_raw_response.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        geocode_check_php = await response.parse()
        assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.geocode_check_php.with_streaming_response.check(
            address="address",
            county="county",
            session_id="session_id",
            state="state",
            township="township",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            geocode_check_php = await response.parse()
            assert_matches_type(GeocodeCheckPhpCheckResponse, geocode_check_php, path=["response"])

        assert cast(Any, response.is_closed) is True
