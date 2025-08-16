# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import LoginAuthenticateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLogin:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_authenticate(self, client: Lodestarmcp) -> None:
        login = client.login.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        )
        assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_authenticate(self, client: Lodestarmcp) -> None:
        response = client.login.with_raw_response.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        login = response.parse()
        assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_authenticate(self, client: Lodestarmcp) -> None:
        with client.login.with_streaming_response.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            login = response.parse()
            assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLogin:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_authenticate(self, async_client: AsyncLodestarmcp) -> None:
        login = await async_client.login.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        )
        assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_authenticate(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.login.with_raw_response.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        login = await response.parse()
        assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_authenticate(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.login.with_streaming_response.authenticate(
            password="abcd1234!",
            username="example@lodestarss.com",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            login = await response.parse()
            assert_matches_type(LoginAuthenticateResponse, login, path=["response"])

        assert cast(Any, response.is_closed) is True
