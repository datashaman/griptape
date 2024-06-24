from __future__ import annotations

from typing import Callable, Optional
from attrs import field, Factory, define
import requests

from griptape.artifacts import TextArtifact
from griptape.drivers import BaseWebScraperDriver


@define
class ProxyWebScraperDriver(BaseWebScraperDriver):
    proxies: dict = field(kw_only=True, metadata={"serializable": False})
    params: dict = field(default=Factory(dict), kw_only=True, metadata={"serializable": True})
    cache_get: Callable[[str], Optional[TextArtifact]] = field(
        kw_only=True, default=None, metadata={"serializable": False}
    )
    cache_set: Callable[[str, str, str], None] = field(kw_only=True, default=None, metadata={"serializable": False})

    def scrape_url(self, url: str) -> TextArtifact:
        import hashlib

        # hash the url to get a unique name for the file
        hashed_name = hashlib.md5(url.encode()).hexdigest()
        try:
            cache = self.cache_get(hashed_name) if self.cache_get is not None else None
            if cache is not None:
                return cache
        except Exception as e:
            print(e)
            pass
        response = requests.get(url, proxies=self.proxies, **self.params)
        try:
            if self.cache_set is not None:
                self.cache_set(response.text, url, hashed_name)
        except Exception as e:
            print(e)
            pass
        return TextArtifact(response.text)
