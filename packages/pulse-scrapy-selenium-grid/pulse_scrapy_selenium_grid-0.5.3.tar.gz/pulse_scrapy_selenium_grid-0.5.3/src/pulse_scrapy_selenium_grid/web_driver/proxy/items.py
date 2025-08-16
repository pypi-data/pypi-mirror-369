from dataclasses import dataclass
from typing import Optional

from scrapy.settings import Settings


@dataclass
class ProxyConfig:
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def from_settings(cls, settings: Settings) -> Optional["ProxyConfig"]:
        if settings.get("PROXY_ENABLED") is not True:
            return

        cfg = cls(
            host=settings.get("PROXY_HOST"),
            port=settings.get("PROXY_PORT"),
            username=settings.get("PROXY_USERNAME"),
            password=settings.get("PROXY_PASSWORD"),
        )
        return cfg
