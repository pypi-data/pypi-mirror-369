from http.client import responses
from json.decoder import JSONDecodeError
from logging import getLogger
from typing import Any

import requests

from wowool.portal.client.error import PortalApiError

logger = getLogger(__name__)


class Service:
    def __init__(self, url: str, headers: dict[str, str]):
        self.url = url
        self.headers = headers

    def _url_for(self, url):
        return f"{self.url}/v1/{url}"

    def get(self, url: str, **kwargs):
        logger.debug(f"Request: GET {url}")
        response = requests.get(
            self._url_for(url),
            headers=self.headers,
            **kwargs,
        )
        return self._validate_response(response)

    def post(self, url: str, json: dict[str, Any], **kwargs):
        logger.debug(f"Request: POST {url}")
        response = requests.post(
            self._url_for(url),
            json=json,
            headers=self.headers,
            **kwargs,
        )
        return self._validate_response(response)

    def _validate_response(self, response: requests.Response):
        if response.ok:
            return response
        self._raise_api_error(response)

    def _raise_api_error(self, response: requests.Response):
        try:
            error_raw: dict[str, Any] = response.json()
        except JSONDecodeError:
            logger.error(f"No JSON was returned: {response.status_code} - {responses[response.status_code]}")
            raise

        type = error_raw.get("type", "UnknownError")
        message = error_raw.get("message", "Unknown error")
        details = error_raw.get("details", None)
        raise PortalApiError(type, message, response.status_code, details)
