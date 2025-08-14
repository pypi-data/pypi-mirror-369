# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from openint import Openint, AsyncOpenint
from tests.utils import assert_matches_type
from openint.types import (
    ListEventsResponse,
    CreateTokenResponse,
    GetConnectionResponse,
    ListCustomersResponse,
    GetCurrentUserResponse,
    ListConnectorsResponse,
    UpsertCustomerResponse,
    CheckConnectionResponse,
    ListConnectionsResponse,
    CreateConnectionResponse,
    DeleteConnectionResponse,
    GetConectorConfigResponse,
    GetMessageTemplateResponse,
    ListConnectionConfigsResponse,
    ListConnnectorConfigsResponse,
    CreateConnnectorConfigResponse,
    UpsertConnnectorConfigResponse,
)
from openint.pagination import SyncOffsetPagination, AsyncOffsetPagination

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClient:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_check_connection(self, client: Openint) -> None:
        client_ = client.check_connection(
            "conn_",
        )
        assert_matches_type(CheckConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_check_connection(self, client: Openint) -> None:
        response = client.with_raw_response.check_connection(
            "conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CheckConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_check_connection(self, client: Openint) -> None:
        with client.with_streaming_response.check_connection(
            "conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CheckConnectionResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_check_connection(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.with_raw_response.check_connection(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_connection(self, client: Openint) -> None:
        client_ = client.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        )
        assert_matches_type(CreateConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_connection_with_all_params(self, client: Openint) -> None:
        client_ = client.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={
                "connector_name": "accelo",
                "settings": {
                    "oauth": {
                        "created_at": "created_at",
                        "credentials": {
                            "access_token": "access_token",
                            "client_id": "client_id",
                            "expires_at": "expires_at",
                            "expires_in": 0,
                            "raw": {"foo": "bar"},
                            "refresh_token": "refresh_token",
                            "scope": "scope",
                            "token_type": "token_type",
                        },
                        "last_fetched_at": "last_fetched_at",
                        "metadata": {"foo": "bar"},
                        "updated_at": "updated_at",
                    },
                    "subdomain": "https://26f1kl_-n-71.api.accelo.com",
                    "access_token": "access_token",
                },
            },
            check_connection=True,
            metadata={"foo": "bar"},
        )
        assert_matches_type(CreateConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_connection(self, client: Openint) -> None:
        response = client.with_raw_response.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CreateConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_connection(self, client: Openint) -> None:
        with client.with_streaming_response.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CreateConnectionResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_connnector_config(self, client: Openint) -> None:
        client_ = client.create_connnector_config(
            connector_name="connector_name",
        )
        assert_matches_type(CreateConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_connnector_config_with_all_params(self, client: Openint) -> None:
        client_ = client.create_connnector_config(
            connector_name="connector_name",
            config={"foo": "bar"},
            disabled=True,
            display_name="display_name",
            metadata={"foo": "bar"},
        )
        assert_matches_type(CreateConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_connnector_config(self, client: Openint) -> None:
        response = client.with_raw_response.create_connnector_config(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CreateConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_connnector_config(self, client: Openint) -> None:
        with client.with_streaming_response.create_connnector_config(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CreateConnnectorConfigResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_token(self, client: Openint) -> None:
        client_ = client.create_token(
            customer_id="x",
        )
        assert_matches_type(CreateTokenResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_token_with_all_params(self, client: Openint) -> None:
        client_ = client.create_token(
            customer_id="x",
            connect_options={
                "connector_names": ["accelo"],
                "debug": True,
                "is_embedded": True,
                "return_url": "return_url",
                "view": "add",
            },
            validity_in_seconds=0,
        )
        assert_matches_type(CreateTokenResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_token(self, client: Openint) -> None:
        response = client.with_raw_response.create_token(
            customer_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(CreateTokenResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_token(self, client: Openint) -> None:
        with client.with_streaming_response.create_token(
            customer_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(CreateTokenResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_token(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            client.with_raw_response.create_token(
                customer_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_connection(self, client: Openint) -> None:
        client_ = client.delete_connection(
            "conn_",
        )
        assert_matches_type(DeleteConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_connection(self, client: Openint) -> None:
        response = client.with_raw_response.delete_connection(
            "conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(DeleteConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_connection(self, client: Openint) -> None:
        with client.with_streaming_response.delete_connection(
            "conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(DeleteConnectionResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_connection(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.with_raw_response.delete_connection(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_conector_config(self, client: Openint) -> None:
        client_ = client.get_conector_config(
            id="ccfg_",
        )
        assert_matches_type(GetConectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_conector_config_with_all_params(self, client: Openint) -> None:
        client_ = client.get_conector_config(
            id="ccfg_",
            expand=["connector"],
        )
        assert_matches_type(GetConectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_conector_config(self, client: Openint) -> None:
        response = client.with_raw_response.get_conector_config(
            id="ccfg_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(GetConectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_conector_config(self, client: Openint) -> None:
        with client.with_streaming_response.get_conector_config(
            id="ccfg_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(GetConectorConfigResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_conector_config(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.with_raw_response.get_conector_config(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connection(self, client: Openint) -> None:
        client_ = client.get_connection(
            id="conn_",
        )
        assert_matches_type(GetConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_connection_with_all_params(self, client: Openint) -> None:
        client_ = client.get_connection(
            id="conn_",
            expand=["connector"],
            include_secrets=True,
            refresh_policy="none",
        )
        assert_matches_type(GetConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_connection(self, client: Openint) -> None:
        response = client.with_raw_response.get_connection(
            id="conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(GetConnectionResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_connection(self, client: Openint) -> None:
        with client.with_streaming_response.get_connection(
            id="conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(GetConnectionResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_connection(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.with_raw_response.get_connection(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_current_user(self, client: Openint) -> None:
        client_ = client.get_current_user()
        assert_matches_type(GetCurrentUserResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_current_user(self, client: Openint) -> None:
        response = client.with_raw_response.get_current_user()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(GetCurrentUserResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_current_user(self, client: Openint) -> None:
        with client.with_streaming_response.get_current_user() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(GetCurrentUserResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_message_template(self, client: Openint) -> None:
        client_ = client.get_message_template(
            customer_id="customer_id",
        )
        assert_matches_type(GetMessageTemplateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_message_template_with_all_params(self, client: Openint) -> None:
        client_ = client.get_message_template(
            customer_id="customer_id",
            language="javascript",
            use_environment_variables=True,
        )
        assert_matches_type(GetMessageTemplateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_message_template(self, client: Openint) -> None:
        response = client.with_raw_response.get_message_template(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(GetMessageTemplateResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_message_template(self, client: Openint) -> None:
        with client.with_streaming_response.get_message_template(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(GetMessageTemplateResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connection_configs(self, client: Openint) -> None:
        client_ = client.list_connection_configs()
        assert_matches_type(SyncOffsetPagination[ListConnectionConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connection_configs_with_all_params(self, client: Openint) -> None:
        client_ = client.list_connection_configs(
            connector_names=["accelo"],
            expand=["connector"],
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(SyncOffsetPagination[ListConnectionConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_connection_configs(self, client: Openint) -> None:
        response = client.with_raw_response.list_connection_configs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListConnectionConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_connection_configs(self, client: Openint) -> None:
        with client.with_streaming_response.list_connection_configs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListConnectionConfigsResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connections(self, client: Openint) -> None:
        client_ = client.list_connections()
        assert_matches_type(SyncOffsetPagination[ListConnectionsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connections_with_all_params(self, client: Openint) -> None:
        client_ = client.list_connections(
            connector_config_id="ccfg_",
            connector_names=["accelo"],
            customer_id="customer_id",
            expand=["connector"],
            include_secrets=True,
            limit=0,
            offset=0,
            refresh_policy="none",
            search_query="search_query",
        )
        assert_matches_type(SyncOffsetPagination[ListConnectionsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_connections(self, client: Openint) -> None:
        response = client.with_raw_response.list_connections()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListConnectionsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_connections(self, client: Openint) -> None:
        with client.with_streaming_response.list_connections() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListConnectionsResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connectors(self, client: Openint) -> None:
        client_ = client.list_connectors()
        assert_matches_type(SyncOffsetPagination[ListConnectorsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connectors_with_all_params(self, client: Openint) -> None:
        client_ = client.list_connectors(
            expand=["schemas"],
            limit=0,
            offset=0,
        )
        assert_matches_type(SyncOffsetPagination[ListConnectorsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_connectors(self, client: Openint) -> None:
        response = client.with_raw_response.list_connectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListConnectorsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_connectors(self, client: Openint) -> None:
        with client.with_streaming_response.list_connectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListConnectorsResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connnector_configs(self, client: Openint) -> None:
        client_ = client.list_connnector_configs()
        assert_matches_type(SyncOffsetPagination[ListConnnectorConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_connnector_configs_with_all_params(self, client: Openint) -> None:
        client_ = client.list_connnector_configs(
            connector_names=["accelo"],
            expand=["connector"],
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(SyncOffsetPagination[ListConnnectorConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_connnector_configs(self, client: Openint) -> None:
        response = client.with_raw_response.list_connnector_configs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListConnnectorConfigsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_connnector_configs(self, client: Openint) -> None:
        with client.with_streaming_response.list_connnector_configs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListConnnectorConfigsResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_customers(self, client: Openint) -> None:
        client_ = client.list_customers()
        assert_matches_type(SyncOffsetPagination[ListCustomersResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_customers_with_all_params(self, client: Openint) -> None:
        client_ = client.list_customers(
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(SyncOffsetPagination[ListCustomersResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_customers(self, client: Openint) -> None:
        response = client.with_raw_response.list_customers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListCustomersResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_customers(self, client: Openint) -> None:
        with client.with_streaming_response.list_customers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListCustomersResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events(self, client: Openint) -> None:
        client_ = client.list_events()
        assert_matches_type(SyncOffsetPagination[ListEventsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events_with_all_params(self, client: Openint) -> None:
        client_ = client.list_events(
            expand=["prompt"],
            limit=0,
            offset=0,
            search_query="search_query",
            since="since",
        )
        assert_matches_type(SyncOffsetPagination[ListEventsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_events(self, client: Openint) -> None:
        response = client.with_raw_response.list_events()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(SyncOffsetPagination[ListEventsResponse], client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_events(self, client: Openint) -> None:
        with client.with_streaming_response.list_events() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(SyncOffsetPagination[ListEventsResponse], client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_connnector_config(self, client: Openint) -> None:
        client_ = client.upsert_connnector_config(
            id="ccfg_",
        )
        assert_matches_type(UpsertConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_connnector_config_with_all_params(self, client: Openint) -> None:
        client_ = client.upsert_connnector_config(
            id="ccfg_",
            config={"foo": "bar"},
            disabled=True,
            display_name="display_name",
        )
        assert_matches_type(UpsertConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upsert_connnector_config(self, client: Openint) -> None:
        response = client.with_raw_response.upsert_connnector_config(
            id="ccfg_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(UpsertConnnectorConfigResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upsert_connnector_config(self, client: Openint) -> None:
        with client.with_streaming_response.upsert_connnector_config(
            id="ccfg_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(UpsertConnnectorConfigResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_upsert_connnector_config(self, client: Openint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.with_raw_response.upsert_connnector_config(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_customer(self, client: Openint) -> None:
        client_ = client.upsert_customer()
        assert_matches_type(UpsertCustomerResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_upsert_customer_with_all_params(self, client: Openint) -> None:
        client_ = client.upsert_customer(
            id="id",
            metadata={"foo": "bar"},
        )
        assert_matches_type(UpsertCustomerResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_upsert_customer(self, client: Openint) -> None:
        response = client.with_raw_response.upsert_customer()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client_ = response.parse()
        assert_matches_type(UpsertCustomerResponse, client_, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_upsert_customer(self, client: Openint) -> None:
        with client.with_streaming_response.upsert_customer() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client_ = response.parse()
            assert_matches_type(UpsertCustomerResponse, client_, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncClient:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_check_connection(self, async_client: AsyncOpenint) -> None:
        client = await async_client.check_connection(
            "conn_",
        )
        assert_matches_type(CheckConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_check_connection(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.check_connection(
            "conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CheckConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_check_connection(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.check_connection(
            "conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CheckConnectionResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_check_connection(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.with_raw_response.check_connection(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_connection(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        )
        assert_matches_type(CreateConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_connection_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={
                "connector_name": "accelo",
                "settings": {
                    "oauth": {
                        "created_at": "created_at",
                        "credentials": {
                            "access_token": "access_token",
                            "client_id": "client_id",
                            "expires_at": "expires_at",
                            "expires_in": 0,
                            "raw": {"foo": "bar"},
                            "refresh_token": "refresh_token",
                            "scope": "scope",
                            "token_type": "token_type",
                        },
                        "last_fetched_at": "last_fetched_at",
                        "metadata": {"foo": "bar"},
                        "updated_at": "updated_at",
                    },
                    "subdomain": "https://26f1kl_-n-71.api.accelo.com",
                    "access_token": "access_token",
                },
            },
            check_connection=True,
            metadata={"foo": "bar"},
        )
        assert_matches_type(CreateConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_connection(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CreateConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_connection(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.create_connection(
            connector_config_id="ccfg_",
            customer_id="customer_id",
            data={"connector_name": "accelo"},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CreateConnectionResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_connnector_config(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_connnector_config(
            connector_name="connector_name",
        )
        assert_matches_type(CreateConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_connnector_config_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_connnector_config(
            connector_name="connector_name",
            config={"foo": "bar"},
            disabled=True,
            display_name="display_name",
            metadata={"foo": "bar"},
        )
        assert_matches_type(CreateConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_connnector_config(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.create_connnector_config(
            connector_name="connector_name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CreateConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_connnector_config(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.create_connnector_config(
            connector_name="connector_name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CreateConnnectorConfigResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_token(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_token(
            customer_id="x",
        )
        assert_matches_type(CreateTokenResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_token_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.create_token(
            customer_id="x",
            connect_options={
                "connector_names": ["accelo"],
                "debug": True,
                "is_embedded": True,
                "return_url": "return_url",
                "view": "add",
            },
            validity_in_seconds=0,
        )
        assert_matches_type(CreateTokenResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_token(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.create_token(
            customer_id="x",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(CreateTokenResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_token(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.create_token(
            customer_id="x",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(CreateTokenResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_token(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `customer_id` but received ''"):
            await async_client.with_raw_response.create_token(
                customer_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_connection(self, async_client: AsyncOpenint) -> None:
        client = await async_client.delete_connection(
            "conn_",
        )
        assert_matches_type(DeleteConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_connection(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.delete_connection(
            "conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(DeleteConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_connection(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.delete_connection(
            "conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(DeleteConnectionResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_connection(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.with_raw_response.delete_connection(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_conector_config(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_conector_config(
            id="ccfg_",
        )
        assert_matches_type(GetConectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_conector_config_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_conector_config(
            id="ccfg_",
            expand=["connector"],
        )
        assert_matches_type(GetConectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_conector_config(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.get_conector_config(
            id="ccfg_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(GetConectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_conector_config(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.get_conector_config(
            id="ccfg_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(GetConectorConfigResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_conector_config(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.with_raw_response.get_conector_config(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connection(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_connection(
            id="conn_",
        )
        assert_matches_type(GetConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_connection_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_connection(
            id="conn_",
            expand=["connector"],
            include_secrets=True,
            refresh_policy="none",
        )
        assert_matches_type(GetConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_connection(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.get_connection(
            id="conn_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(GetConnectionResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_connection(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.get_connection(
            id="conn_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(GetConnectionResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_connection(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.with_raw_response.get_connection(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_current_user(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_current_user()
        assert_matches_type(GetCurrentUserResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_current_user(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.get_current_user()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(GetCurrentUserResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_current_user(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.get_current_user() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(GetCurrentUserResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_message_template(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_message_template(
            customer_id="customer_id",
        )
        assert_matches_type(GetMessageTemplateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_message_template_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.get_message_template(
            customer_id="customer_id",
            language="javascript",
            use_environment_variables=True,
        )
        assert_matches_type(GetMessageTemplateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_message_template(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.get_message_template(
            customer_id="customer_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(GetMessageTemplateResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_message_template(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.get_message_template(
            customer_id="customer_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(GetMessageTemplateResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connection_configs(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connection_configs()
        assert_matches_type(AsyncOffsetPagination[ListConnectionConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connection_configs_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connection_configs(
            connector_names=["accelo"],
            expand=["connector"],
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(AsyncOffsetPagination[ListConnectionConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_connection_configs(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_connection_configs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListConnectionConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_connection_configs(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_connection_configs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListConnectionConfigsResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connections(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connections()
        assert_matches_type(AsyncOffsetPagination[ListConnectionsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connections_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connections(
            connector_config_id="ccfg_",
            connector_names=["accelo"],
            customer_id="customer_id",
            expand=["connector"],
            include_secrets=True,
            limit=0,
            offset=0,
            refresh_policy="none",
            search_query="search_query",
        )
        assert_matches_type(AsyncOffsetPagination[ListConnectionsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_connections(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_connections()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListConnectionsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_connections(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_connections() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListConnectionsResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connectors(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connectors()
        assert_matches_type(AsyncOffsetPagination[ListConnectorsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connectors_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connectors(
            expand=["schemas"],
            limit=0,
            offset=0,
        )
        assert_matches_type(AsyncOffsetPagination[ListConnectorsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_connectors(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_connectors()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListConnectorsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_connectors(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_connectors() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListConnectorsResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connnector_configs(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connnector_configs()
        assert_matches_type(AsyncOffsetPagination[ListConnnectorConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_connnector_configs_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_connnector_configs(
            connector_names=["accelo"],
            expand=["connector"],
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(AsyncOffsetPagination[ListConnnectorConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_connnector_configs(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_connnector_configs()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListConnnectorConfigsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_connnector_configs(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_connnector_configs() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListConnnectorConfigsResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_customers(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_customers()
        assert_matches_type(AsyncOffsetPagination[ListCustomersResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_customers_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_customers(
            limit=0,
            offset=0,
            search_query="search_query",
        )
        assert_matches_type(AsyncOffsetPagination[ListCustomersResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_customers(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_customers()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListCustomersResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_customers(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_customers() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListCustomersResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_events()
        assert_matches_type(AsyncOffsetPagination[ListEventsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.list_events(
            expand=["prompt"],
            limit=0,
            offset=0,
            search_query="search_query",
            since="since",
        )
        assert_matches_type(AsyncOffsetPagination[ListEventsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.list_events()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(AsyncOffsetPagination[ListEventsResponse], client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.list_events() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(AsyncOffsetPagination[ListEventsResponse], client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_connnector_config(self, async_client: AsyncOpenint) -> None:
        client = await async_client.upsert_connnector_config(
            id="ccfg_",
        )
        assert_matches_type(UpsertConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_connnector_config_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.upsert_connnector_config(
            id="ccfg_",
            config={"foo": "bar"},
            disabled=True,
            display_name="display_name",
        )
        assert_matches_type(UpsertConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upsert_connnector_config(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.upsert_connnector_config(
            id="ccfg_",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(UpsertConnnectorConfigResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upsert_connnector_config(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.upsert_connnector_config(
            id="ccfg_",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(UpsertConnnectorConfigResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_upsert_connnector_config(self, async_client: AsyncOpenint) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.with_raw_response.upsert_connnector_config(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_customer(self, async_client: AsyncOpenint) -> None:
        client = await async_client.upsert_customer()
        assert_matches_type(UpsertCustomerResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_upsert_customer_with_all_params(self, async_client: AsyncOpenint) -> None:
        client = await async_client.upsert_customer(
            id="id",
            metadata={"foo": "bar"},
        )
        assert_matches_type(UpsertCustomerResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_upsert_customer(self, async_client: AsyncOpenint) -> None:
        response = await async_client.with_raw_response.upsert_customer()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        client = await response.parse()
        assert_matches_type(UpsertCustomerResponse, client, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_upsert_customer(self, async_client: AsyncOpenint) -> None:
        async with async_client.with_streaming_response.upsert_customer() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            client = await response.parse()
            assert_matches_type(UpsertCustomerResponse, client, path=["response"])

        assert cast(Any, response.is_closed) is True
