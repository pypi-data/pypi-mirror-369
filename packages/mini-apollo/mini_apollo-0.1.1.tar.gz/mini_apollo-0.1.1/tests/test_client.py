import hashlib
import hmac

import pytest
import responses
from aioresponses import aioresponses

from mini_apollo import ApolloClient


def test_apollo_client_init():
    client = ApolloClient("http://localhost:8080", "test-app", "secret")
    assert client._server_url == "http://localhost:8080"
    assert client._app_id == "test-app"
    assert client._secret == "secret"


def test_apollo_client_init_without_secret():
    client = ApolloClient("http://localhost:8080", "test-app")
    assert client._server_url == "http://localhost:8080"
    assert client._app_id == "test-app"
    assert client._secret is None


@responses.activate
def test_fetch_config_success(apollo_client, mock_config_response):
    responses.add(
        responses.GET,
        "http://localhost:8080/configs/test-app/default/application",
        json=mock_config_response,
        status=200
    )

    config = apollo_client.fetch_config()
    assert config == mock_config_response["configurations"]


@responses.activate
def test_fetch_config_with_params(apollo_client, mock_config_response):
    responses.add(
        responses.GET,
        "http://localhost:8080/configs/test-app/prod/custom",
        json=mock_config_response,
        status=200
    )

    config = apollo_client.fetch_config(cluster="prod", namespace="custom")
    assert config == mock_config_response["configurations"]


@responses.activate
def test_fetch_config_without_auth(apollo_client_no_auth, mock_config_response):
    responses.add(
        responses.GET,
        "http://localhost:8080/configs/test-app/default/application",
        json=mock_config_response,
        status=200
    )

    config = apollo_client_no_auth.fetch_config()
    assert config == mock_config_response["configurations"]


@responses.activate
def test_fetch_config_http_error(apollo_client):
    responses.add(
        responses.GET,
        "http://localhost:8080/configs/test-app/default/application",
        status=404
    )

    with pytest.raises(Exception):
        apollo_client.fetch_config()


@pytest.mark.asyncio
async def test_async_fetch_config_success(apollo_client, mock_config_response):
    with aioresponses() as m:
        m.get(
            "http://localhost:8080/configs/test-app/default/application",
            payload=mock_config_response
        )

        config = await apollo_client.async_fetch_config()
        assert config == mock_config_response["configurations"]


@pytest.mark.asyncio
async def test_async_fetch_config_with_params(apollo_client, mock_config_response):
    with aioresponses() as m:
        m.get(
            "http://localhost:8080/configs/test-app/prod/custom",
            payload=mock_config_response
        )

        config = await apollo_client.async_fetch_config(cluster="prod", namespace="custom")
        assert config == mock_config_response["configurations"]


@pytest.mark.asyncio
async def test_async_fetch_config_without_auth(apollo_client_no_auth, mock_config_response):
    with aioresponses() as m:
        m.get(
            "http://localhost:8080/configs/test-app/default/application",
            payload=mock_config_response
        )

        config = await apollo_client_no_auth.async_fetch_config()
        assert config == mock_config_response["configurations"]


def test_build_auth_headers(mocker):
    url = "http://localhost:8080/configs/test-app/default/application"
    app_id = "test-app"
    secret = "test-secret"

    mocker.patch('time.time', return_value=1234567890.123)
    headers = ApolloClient._build_auth_headers(url, app_id, secret)

    expected_timestamp = "1234567890123"
    expected_string_to_sign = f"{expected_timestamp}\n/configs/test-app/default/application"
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        expected_string_to_sign.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()

    assert headers["Authorization"] == f"{app_id}:{expected_signature}"
    assert headers["Timestamp"] == expected_timestamp


def test_build_auth_headers_with_query(mocker):
    url = "http://localhost:8080/configs/test-app/default/application?ip=127.0.0.1"
    app_id = "test-app"
    secret = "test-secret"

    mocker.patch('time.time', return_value=1234567890.123)
    headers = ApolloClient._build_auth_headers(url, app_id, secret)

    expected_timestamp = "1234567890123"
    expected_string_to_sign = f"{expected_timestamp}\n/configs/test-app/default/application?ip=127.0.0.1"
    expected_signature = hmac.new(
        secret.encode("utf-8"),
        expected_string_to_sign.encode("utf-8"),
        hashlib.sha1
    ).hexdigest()

    assert headers["Authorization"] == f"{app_id}:{expected_signature}"
    assert headers["Timestamp"] == expected_timestamp
