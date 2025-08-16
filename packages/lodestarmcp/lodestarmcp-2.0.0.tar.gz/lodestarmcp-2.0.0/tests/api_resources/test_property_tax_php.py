# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lodestarmcp import Lodestarmcp, AsyncLodestarmcp
from tests.utils import assert_matches_type
from lodestarmcp.types import PropertyTaxPhpRetrieveResponse
from lodestarmcp._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPropertyTaxPhp:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Lodestarmcp) -> None:
        property_tax_php = client.property_tax_php.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        )
        assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Lodestarmcp) -> None:
        response = client.property_tax_php.with_raw_response.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        property_tax_php = response.parse()
        assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Lodestarmcp) -> None:
        with client.property_tax_php.with_streaming_response.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            property_tax_php = response.parse()
            assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncPropertyTaxPhp:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLodestarmcp) -> None:
        property_tax_php = await async_client.property_tax_php.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        )
        assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLodestarmcp) -> None:
        response = await async_client.property_tax_php.with_raw_response.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        property_tax_php = await response.parse()
        assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLodestarmcp) -> None:
        async with async_client.property_tax_php.with_streaming_response.retrieve(
            address="address",
            city="city",
            close_date=parse_date("2019-12-27"),
            county="county",
            file_name="file_name",
            purchase_price=0,
            session_id="session_id",
            state="state",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            property_tax_php = await response.parse()
            assert_matches_type(PropertyTaxPhpRetrieveResponse, property_tax_php, path=["response"])

        assert cast(Any, response.is_closed) is True
