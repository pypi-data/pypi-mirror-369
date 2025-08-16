import json
import logging
import os
import re
import uuid
from datetime import datetime

import requests
from cachetools import TTLCache

from .classes import DopplerJson

logger = logging.getLogger(__name__)


class Doppler:
    def __init__(
        self, project: str, config: str, token: str = None, ttl: int = 60 * 60, defaults: dict[str, object] = None
    ):
        self.project: str = project
        self.config: str = config
        self.token: str = token or os.getenv("DOPPLER_TOKEN")

        self.defaults: dict[str, object] = defaults or {}

        self.cache_key: str = f"{self.project}/{self.config}"

        self.cache: TTLCache = TTLCache(maxsize=100, ttl=ttl)

    @property
    def url(self):
        return "https://api.doppler.com/v3/configs/config/secrets"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    @property
    def params(self):
        return {
            "project": self.project,
            "config": self.config,
        }

    def invalidate_cache(self):
        del self.cache[self.cache_key]

    def _get(self) -> dict:
        if self.cache_key not in self.cache:
            logger.info("%s/%s > fetching secrets", self.project, self.config)

            response = requests.get(
                self.url,
                headers=self.headers,
                params=self.params,
            )

            if response.status_code != 200:
                logger.error("%s/%s > failed to fetch secrets: %s", self.project, self.config, response.text)
                response.raise_for_status()

            self.cache[self.cache_key] = response.json()

        return self.cache[self.cache_key]

    def get(self, name: str) -> object:
        secrets = self._get()["secrets"]

        if name not in secrets:
            if name in self.defaults:
                return self.defaults[name]
            else:
                raise KeyError(f"{name} is not a valid secret")

        secret = secrets[name]
        value = secret["computed"]
        type = secret["computedValueType"]["type"]

        try:
            if type == "boolean":
                return value.lower() == "true"
            elif type == "integer":
                return int(value)
            elif type == "decimal":
                return float(value)
            elif type == "date8601":
                return datetime.strptime(value, "%Y-%m-%d").date()
            elif type == "datetime8601":
                return datetime.strptime(value, "%Y-%m-%d %H:%M:%S %z")
            elif type.startswith("uuid"):
                return uuid.UUID(value)
            elif type.startswith("json"):
                return DopplerJson(name, value)
            else:
                if "," in value:
                    return value.split(",")

                return value
        except KeyError:
            raise KeyError(f"{name} is not a valid secret")

    def __getattribute__(self, name: str):
        if bool(re.fullmatch(r"[A-Z_]+", name)):
            return self.get(name)

        return super().__getattribute__(name)

    def __getitem__(self, name: str) -> object:
        return self.get(name)
