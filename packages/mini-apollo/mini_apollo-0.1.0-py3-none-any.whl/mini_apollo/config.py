import threading
import time
from collections.abc import Mapping

from .client import ApolloClient


class ApolloConfig(Mapping):

    def __init__(
        self,
        client: ApolloClient,
        cluster: str = "default",
        namespace: str = "application",
        auto_refresh: bool = False,
        refresh_interval: int = 30,
    ):
        self._client = client
        self._cluster = cluster
        self._namespace = namespace
        self._auto_refresh = auto_refresh
        self._refresh_interval = refresh_interval
        self._update_lock = threading.Lock()

        self._config = self._client.fetch_config(
            cluster=cluster,
            namespace=namespace
        )

        if self._auto_refresh:
            self._start_refresh_thread()

    def __getitem__(self, key):
        return self._config[key]

    def __iter__(self):
        return iter(self._config)

    def __len__(self):
        return len(self._config)

    def __contains__(self, key):
        return key in self._config

    def _start_refresh_thread(self):
        update_thread = threading.Thread(target=self._refresh_config)
        update_thread.daemon = True
        update_thread.start()

    def _refresh_config(self):
        while True:
            time.sleep(self._refresh_interval)
            config = self._client.fetch_config(
                cluster=self._cluster,
                namespace=self._namespace,
            )
            with self._update_lock:
                self._config = config
