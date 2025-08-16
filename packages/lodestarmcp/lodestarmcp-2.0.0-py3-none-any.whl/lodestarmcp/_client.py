# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Headers,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import (
    login,
    counties_php,
    questions_php,
    townships_php,
    sub_agents_php,
    endorsements_php,
    property_tax_php,
    geocode_check_php,
    appraisal_modifiers_php,
    closing_cost_calculations_php,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Lodestarmcp",
    "AsyncLodestarmcp",
    "Client",
    "AsyncClient",
]


class Lodestarmcp(SyncAPIClient):
    login: login.LoginResource
    closing_cost_calculations_php: closing_cost_calculations_php.ClosingCostCalculationsPhpResource
    property_tax_php: property_tax_php.PropertyTaxPhpResource
    endorsements_php: endorsements_php.EndorsementsPhpResource
    appraisal_modifiers_php: appraisal_modifiers_php.AppraisalModifiersPhpResource
    sub_agents_php: sub_agents_php.SubAgentsPhpResource
    counties_php: counties_php.CountiesPhpResource
    townships_php: townships_php.TownshipsPhpResource
    questions_php: questions_php.QuestionsPhpResource
    geocode_check_php: geocode_check_php.GeocodeCheckPhpResource
    with_raw_response: LodestarmcpWithRawResponse
    with_streaming_response: LodestarmcpWithStreamedResponse

    # client options
    api_key: str | None
    client_name: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        client_name: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Lodestarmcp client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `LODESTARMCP_API_KEY`
        - `client_name` from `LODESTARMCP_CLIENT_NAME`
        """
        if api_key is None:
            api_key = os.environ.get("LODESTARMCP_API_KEY")
        self.api_key = api_key

        if client_name is None:
            client_name = os.environ.get("LODESTARMCP_CLIENT_NAME") or "LodeStar_Demo"
        self.client_name = client_name

        if base_url is None:
            base_url = os.environ.get("LODESTARMCP_BASE_URL")
        if base_url is None:
            base_url = f"https://www.lodestarss.com/Live/{client_name}/"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.login = login.LoginResource(self)
        self.closing_cost_calculations_php = closing_cost_calculations_php.ClosingCostCalculationsPhpResource(self)
        self.property_tax_php = property_tax_php.PropertyTaxPhpResource(self)
        self.endorsements_php = endorsements_php.EndorsementsPhpResource(self)
        self.appraisal_modifiers_php = appraisal_modifiers_php.AppraisalModifiersPhpResource(self)
        self.sub_agents_php = sub_agents_php.SubAgentsPhpResource(self)
        self.counties_php = counties_php.CountiesPhpResource(self)
        self.townships_php = townships_php.TownshipsPhpResource(self)
        self.questions_php = questions_php.QuestionsPhpResource(self)
        self.geocode_check_php = geocode_check_php.GeocodeCheckPhpResource(self)
        self.with_raw_response = LodestarmcpWithRawResponse(self)
        self.with_streaming_response = LodestarmcpWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.api_key and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        api_key: str | None = None,
        client_name: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            client_name=client_name or self.client_name,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncLodestarmcp(AsyncAPIClient):
    login: login.AsyncLoginResource
    closing_cost_calculations_php: closing_cost_calculations_php.AsyncClosingCostCalculationsPhpResource
    property_tax_php: property_tax_php.AsyncPropertyTaxPhpResource
    endorsements_php: endorsements_php.AsyncEndorsementsPhpResource
    appraisal_modifiers_php: appraisal_modifiers_php.AsyncAppraisalModifiersPhpResource
    sub_agents_php: sub_agents_php.AsyncSubAgentsPhpResource
    counties_php: counties_php.AsyncCountiesPhpResource
    townships_php: townships_php.AsyncTownshipsPhpResource
    questions_php: questions_php.AsyncQuestionsPhpResource
    geocode_check_php: geocode_check_php.AsyncGeocodeCheckPhpResource
    with_raw_response: AsyncLodestarmcpWithRawResponse
    with_streaming_response: AsyncLodestarmcpWithStreamedResponse

    # client options
    api_key: str | None
    client_name: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        client_name: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncLodestarmcp client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `LODESTARMCP_API_KEY`
        - `client_name` from `LODESTARMCP_CLIENT_NAME`
        """
        if api_key is None:
            api_key = os.environ.get("LODESTARMCP_API_KEY")
        self.api_key = api_key

        if client_name is None:
            client_name = os.environ.get("LODESTARMCP_CLIENT_NAME") or "LodeStar_Demo"
        self.client_name = client_name

        if base_url is None:
            base_url = os.environ.get("LODESTARMCP_BASE_URL")
        if base_url is None:
            base_url = f"https://www.lodestarss.com/Live/{client_name}/"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.login = login.AsyncLoginResource(self)
        self.closing_cost_calculations_php = closing_cost_calculations_php.AsyncClosingCostCalculationsPhpResource(self)
        self.property_tax_php = property_tax_php.AsyncPropertyTaxPhpResource(self)
        self.endorsements_php = endorsements_php.AsyncEndorsementsPhpResource(self)
        self.appraisal_modifiers_php = appraisal_modifiers_php.AsyncAppraisalModifiersPhpResource(self)
        self.sub_agents_php = sub_agents_php.AsyncSubAgentsPhpResource(self)
        self.counties_php = counties_php.AsyncCountiesPhpResource(self)
        self.townships_php = townships_php.AsyncTownshipsPhpResource(self)
        self.questions_php = questions_php.AsyncQuestionsPhpResource(self)
        self.geocode_check_php = geocode_check_php.AsyncGeocodeCheckPhpResource(self)
        self.with_raw_response = AsyncLodestarmcpWithRawResponse(self)
        self.with_streaming_response = AsyncLodestarmcpWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if api_key is None:
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    @override
    def _validate_headers(self, headers: Headers, custom_headers: Headers) -> None:
        if self.api_key and headers.get("Authorization"):
            return
        if isinstance(custom_headers.get("Authorization"), Omit):
            return

        raise TypeError(
            '"Could not resolve authentication method. Expected the api_key to be set. Or for the `Authorization` headers to be explicitly omitted"'
        )

    def copy(
        self,
        *,
        api_key: str | None = None,
        client_name: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            client_name=client_name or self.client_name,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class LodestarmcpWithRawResponse:
    def __init__(self, client: Lodestarmcp) -> None:
        self.login = login.LoginResourceWithRawResponse(client.login)
        self.closing_cost_calculations_php = (
            closing_cost_calculations_php.ClosingCostCalculationsPhpResourceWithRawResponse(
                client.closing_cost_calculations_php
            )
        )
        self.property_tax_php = property_tax_php.PropertyTaxPhpResourceWithRawResponse(client.property_tax_php)
        self.endorsements_php = endorsements_php.EndorsementsPhpResourceWithRawResponse(client.endorsements_php)
        self.appraisal_modifiers_php = appraisal_modifiers_php.AppraisalModifiersPhpResourceWithRawResponse(
            client.appraisal_modifiers_php
        )
        self.sub_agents_php = sub_agents_php.SubAgentsPhpResourceWithRawResponse(client.sub_agents_php)
        self.counties_php = counties_php.CountiesPhpResourceWithRawResponse(client.counties_php)
        self.townships_php = townships_php.TownshipsPhpResourceWithRawResponse(client.townships_php)
        self.questions_php = questions_php.QuestionsPhpResourceWithRawResponse(client.questions_php)
        self.geocode_check_php = geocode_check_php.GeocodeCheckPhpResourceWithRawResponse(client.geocode_check_php)


class AsyncLodestarmcpWithRawResponse:
    def __init__(self, client: AsyncLodestarmcp) -> None:
        self.login = login.AsyncLoginResourceWithRawResponse(client.login)
        self.closing_cost_calculations_php = (
            closing_cost_calculations_php.AsyncClosingCostCalculationsPhpResourceWithRawResponse(
                client.closing_cost_calculations_php
            )
        )
        self.property_tax_php = property_tax_php.AsyncPropertyTaxPhpResourceWithRawResponse(client.property_tax_php)
        self.endorsements_php = endorsements_php.AsyncEndorsementsPhpResourceWithRawResponse(client.endorsements_php)
        self.appraisal_modifiers_php = appraisal_modifiers_php.AsyncAppraisalModifiersPhpResourceWithRawResponse(
            client.appraisal_modifiers_php
        )
        self.sub_agents_php = sub_agents_php.AsyncSubAgentsPhpResourceWithRawResponse(client.sub_agents_php)
        self.counties_php = counties_php.AsyncCountiesPhpResourceWithRawResponse(client.counties_php)
        self.townships_php = townships_php.AsyncTownshipsPhpResourceWithRawResponse(client.townships_php)
        self.questions_php = questions_php.AsyncQuestionsPhpResourceWithRawResponse(client.questions_php)
        self.geocode_check_php = geocode_check_php.AsyncGeocodeCheckPhpResourceWithRawResponse(client.geocode_check_php)


class LodestarmcpWithStreamedResponse:
    def __init__(self, client: Lodestarmcp) -> None:
        self.login = login.LoginResourceWithStreamingResponse(client.login)
        self.closing_cost_calculations_php = (
            closing_cost_calculations_php.ClosingCostCalculationsPhpResourceWithStreamingResponse(
                client.closing_cost_calculations_php
            )
        )
        self.property_tax_php = property_tax_php.PropertyTaxPhpResourceWithStreamingResponse(client.property_tax_php)
        self.endorsements_php = endorsements_php.EndorsementsPhpResourceWithStreamingResponse(client.endorsements_php)
        self.appraisal_modifiers_php = appraisal_modifiers_php.AppraisalModifiersPhpResourceWithStreamingResponse(
            client.appraisal_modifiers_php
        )
        self.sub_agents_php = sub_agents_php.SubAgentsPhpResourceWithStreamingResponse(client.sub_agents_php)
        self.counties_php = counties_php.CountiesPhpResourceWithStreamingResponse(client.counties_php)
        self.townships_php = townships_php.TownshipsPhpResourceWithStreamingResponse(client.townships_php)
        self.questions_php = questions_php.QuestionsPhpResourceWithStreamingResponse(client.questions_php)
        self.geocode_check_php = geocode_check_php.GeocodeCheckPhpResourceWithStreamingResponse(
            client.geocode_check_php
        )


class AsyncLodestarmcpWithStreamedResponse:
    def __init__(self, client: AsyncLodestarmcp) -> None:
        self.login = login.AsyncLoginResourceWithStreamingResponse(client.login)
        self.closing_cost_calculations_php = (
            closing_cost_calculations_php.AsyncClosingCostCalculationsPhpResourceWithStreamingResponse(
                client.closing_cost_calculations_php
            )
        )
        self.property_tax_php = property_tax_php.AsyncPropertyTaxPhpResourceWithStreamingResponse(
            client.property_tax_php
        )
        self.endorsements_php = endorsements_php.AsyncEndorsementsPhpResourceWithStreamingResponse(
            client.endorsements_php
        )
        self.appraisal_modifiers_php = appraisal_modifiers_php.AsyncAppraisalModifiersPhpResourceWithStreamingResponse(
            client.appraisal_modifiers_php
        )
        self.sub_agents_php = sub_agents_php.AsyncSubAgentsPhpResourceWithStreamingResponse(client.sub_agents_php)
        self.counties_php = counties_php.AsyncCountiesPhpResourceWithStreamingResponse(client.counties_php)
        self.townships_php = townships_php.AsyncTownshipsPhpResourceWithStreamingResponse(client.townships_php)
        self.questions_php = questions_php.AsyncQuestionsPhpResourceWithStreamingResponse(client.questions_php)
        self.geocode_check_php = geocode_check_php.AsyncGeocodeCheckPhpResourceWithStreamingResponse(
            client.geocode_check_php
        )


Client = Lodestarmcp

AsyncClient = AsyncLodestarmcp
