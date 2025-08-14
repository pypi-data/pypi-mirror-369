import pytest

from mini_apollo import ApolloClient, ApolloConfig


def test_apollo_config_init_basic(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1", "key2": "value2"}

    config = ApolloConfig(mock_client)

    assert config._client == mock_client
    assert config._cluster == "default"
    assert config._namespace == "application"
    assert config._auto_refresh is False
    assert config._refresh_interval == 30
    mock_client.fetch_config.assert_called_once_with(cluster="default", namespace="application")


def test_apollo_config_init_with_params(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1"}

    config = ApolloConfig(
        mock_client,
        cluster="prod",
        namespace="custom",
        auto_refresh=True,
        refresh_interval=60
    )

    assert config._cluster == "prod"
    assert config._namespace == "custom"
    assert config._auto_refresh is True
    assert config._refresh_interval == 60
    mock_client.fetch_config.assert_called_once_with(cluster="prod", namespace="custom")


def test_apollo_config_getitem(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1", "key2": "value2"}

    config = ApolloConfig(mock_client)

    assert config["key1"] == "value1"
    assert config["key2"] == "value2"


def test_apollo_config_getitem_key_error(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1"}

    config = ApolloConfig(mock_client)

    with pytest.raises(KeyError):
        _ = config["nonexistent_key"]


def test_apollo_config_iter(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1", "key2": "value2"}

    config = ApolloConfig(mock_client)

    keys = list(config)
    assert set(keys) == {"key1", "key2"}


def test_apollo_config_len(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1", "key2": "value2"}

    config = ApolloConfig(mock_client)

    assert len(config) == 2


def test_apollo_config_contains(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1", "key2": "value2"}

    config = ApolloConfig(mock_client)

    assert "key1" in config
    assert "key2" in config
    assert "nonexistent" not in config


def test_apollo_config_auto_refresh_enabled(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1"}

    mock_thread_instance = mocker.Mock()
    mock_thread = mocker.patch("threading.Thread", return_value=mock_thread_instance)

    _ = ApolloConfig(mock_client, auto_refresh=True)

    mock_thread.assert_called_once()
    mock_thread_instance.start.assert_called_once()
    assert mock_thread_instance.daemon is True


def test_apollo_config_auto_refresh_disabled(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {"key1": "value1"}

    mock_thread = mocker.patch("threading.Thread")

    _ = ApolloConfig(mock_client, auto_refresh=False)

    mock_thread.assert_not_called()


def test_apollo_config_refresh_config(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    initial_config = {"key1": "value1"}
    updated_config = {"key1": "updated_value1", "key2": "value2"}

    mock_client.fetch_config.side_effect = [initial_config, updated_config]

    mock_sleep = mocker.patch("time.sleep")

    config = ApolloConfig(mock_client, refresh_interval=10)

    assert config["key1"] == "value1"
    assert len(config) == 1

    mock_sleep.side_effect = [None, KeyboardInterrupt()]

    try:
        config._refresh_config()
    except KeyboardInterrupt:
        pass

    mock_sleep.assert_called_with(10)
    assert mock_client.fetch_config.call_count == 2
    assert config["key1"] == "updated_value1"
    assert config["key2"] == "value2"
    assert len(config) == 2


def test_apollo_config_mapping_interface(mocker):
    mock_client = mocker.Mock(spec=ApolloClient)
    mock_client.fetch_config.return_value = {
        "database.host": "localhost",
        "database.port": "3306",
        "cache.enabled": "true"
    }

    config = ApolloConfig(mock_client)

    assert dict(config) == {
        "database.host": "localhost",
        "database.port": "3306",
        "cache.enabled": "true"
    }

    keys = list(config.keys())
    values = list(config.values())
    items = list(config.items())

    assert set(keys) == {"database.host", "database.port", "cache.enabled"}
    assert set(values) == {"localhost", "3306", "true"}
    assert len(items) == 3
