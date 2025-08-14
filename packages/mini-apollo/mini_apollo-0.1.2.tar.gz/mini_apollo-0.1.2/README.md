# Mini Apollo

A lightweight Python SDK for Apollo Config.

## Installation

```bash
pip install mini-apollo
```

## Quick Start

```python
from mini_apollo import ApolloClient, ApolloConfig

# Basic client setup
client = ApolloClient(
    server_url="http://your-apollo-server:8080",
    app_id="your-app-id",
    secret="your-secret"
)

# Fetch config once
config = client.fetch_config()
print(config.get("db.host"))

# Auto-refreshing config
config = ApolloConfig(
    client=client,
    auto_refresh=True,
    refresh_interval=30
)
print(config["http.timeout"])
```

## Async Support

```python
import asyncio
from mini_apollo import ApolloClient

async def main():
    client = ApolloClient(
        server_url="http://your-apollo-server:8080",
        app_id="your-app-id"
    )
    
    config = await client.async_fetch_config()
    print(config.get("db.host"))

asyncio.run(main())
```

## Configuration Options

```python
from mini_apollo import ApolloClient, ApolloConfig

client = ApolloClient(
    server_url="http://your-apollo-server:8080",
    app_id="your-app-id"
)

# Specify cluster and namespace
config = client.fetch_config(
    cluster="production",
    namespace="database"
)

# Background refresh
config = ApolloConfig(
    client=client,
    cluster="production",
    namespace="database",
    auto_refresh=True,
    refresh_interval=60
)
```

## Pydantic Integration

```python
from functools import cached_property

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mini_apollo import ApolloClient, ApolloConfig


class AppSettings(BaseSettings):
    apollo_server_url: str = Field(..., description="Apollo Server URL")
    apollo_app_id: str = Field(..., description="Apollo App ID")
    apollo_cluster: str = Field("default")
    apollo_namespace: str = Field("application")

    model_config = SettingsConfigDict(env_file=".env")

    @computed_field
    @cached_property
    def apollo_client(self) -> ApolloClient:
        return ApolloClient(
            server_url=self.apollo_server_url,
            app_id=self.apollo_app_id
        )

    @computed_field
    @cached_property
    def apollo_config(self) -> ApolloConfig:
        return ApolloConfig(
            client=self.apollo_client,
            cluster=self.apollo_cluster,
            namespace=self.apollo_namespace,
            auto_refresh=True,
            refresh_interval=30
        )

    @computed_field
    @property
    def db_host(self) -> str:
        return self.apollo_config["db.host"]


# Usage
settings = AppSettings()
print(f"Database host: {settings.db_host}")
```

