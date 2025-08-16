import re
import sys
import textwrap
from typing import Optional, Tuple

import requests

from ts_cli.config.api_config import ApiConfig
from ts_cli.config.publish_artifact_config import PublishArtifactConfig
from ts_cli.config.update_artifact_config import UpdateArtifactConfig
from ts_cli.util.emit import emit_critical, emit_error

REQUEST_TIMEOUT_SECONDS = 60


class TsApiError(Exception):
    """
    For TsApi Failures
    """


class TsApi:
    """
    A simple adapter for the Tetrascience public api
    At the moment, only artifact endpoints are supported
    """

    def __init__(self, config: ApiConfig):
        self.config = config

    @property
    def _api_url(self):
        return self.config.api_url

    @property
    def _request_defaults(self):
        return {
            "verify": self.config.ignore_ssl is not True,
            "headers": self._get_headers(),
        }

    def _get_headers(self):
        headers = {"x-org-slug": self.config.org}
        ts_auth = self.config.auth_token
        if re.compile(r"^([a-z0-9]+-)+[a-z0-9]+$").match(ts_auth, re.IGNORECASE):
            headers["x-api-key"] = ts_auth
        else:
            headers["ts-auth-token"] = ts_auth
        return headers

    @staticmethod
    def _api_error(response):
        try:
            body = response.json()
            message = body.get("message", "Unknown")
            emit_error(f"Response from platform: \n{textwrap.indent(message, '  ')}")
            emit_critical("Exiting")
            sys.exit(1)
        except Exception:
            print(response.text, file=sys.stderr, flush=True)
        return TsApiError(f"HTTP status: {response.status_code}, url: {response.url}")

    def artifact_url(self, config: UpdateArtifactConfig) -> str:
        type_to_url = {
            "connector": "connectors",
            "ids": "ids",
            "protocol": "master-scripts",
            "task-script": "task-scripts",
            "tetraflow": "tetraflows",
        }
        return f"{self._api_url}/artifact/{type_to_url[config.type]}/{config.namespace}/{config.slug}/{config.version}"

    def upload_artifact(self, config: PublishArtifactConfig, artifact_bytes):
        """
        :param config: Artifact configuration
        :param artifact_bytes: ZIP file bytes
        :return: API response body
        """
        params = {
            **({"force": "true"} if config.force else {}),
        }
        response = requests.post(
            self.artifact_url(config),
            **self._request_defaults,
            params=params,
            data=artifact_bytes,
            timeout=600,
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)

    def delete_artifact(self, config: UpdateArtifactConfig):
        """
        :param config:
        :return: API response body
        """
        response = requests.delete(
            self.artifact_url(config),
            **self._request_defaults,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)

    def get_task_script_build_info(self, task_id: str):
        """
        :param task_id: ID of the task build information to retrieve
        :return: API response body
        """
        url = f"{self._api_url}/artifact/builds/{task_id}"
        response = requests.get(
            url, **self._request_defaults, timeout=REQUEST_TIMEOUT_SECONDS
        )
        if response.status_code < 400:
            return response.json()
        raise TsApi._api_error(response)

    def get_task_script_build_logs(self, task_id: str, next_token: Optional[str]):
        """
        :param task_id:
        :param next_token:
        :return:
        """
        url = f"{self._api_url}/artifact/build-logs/{task_id}"
        response = requests.get(
            url,
            **self._request_defaults,
            params={"nextToken": next_token} if next_token is not None else {},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            payload = response.json()
            events = payload.get("events", [])
            next_token = payload.get("nextToken", None)
            return events, next_token
        raise TsApi._api_error(response)

    def get_pipelines_with_artifact(
        self,
        *,
        namespace: str,
        slug: str,
        version: str,
        artifact_type: str,
        page: Optional[int] = None,
    ) -> Tuple[list[dict], Optional[int]]:
        """
        :param page:
        :param namespace:
        :param slug:
        :param version:
        :param artifact_type:
        :return:
        """
        response = requests.get(
            f"{self._api_url}/pipeline/search",
            **self._request_defaults,
            params={
                "protocolNamespace": namespace,
                "protocolName": slug,
                "protocolVersion": version,
                "artifactType": artifact_type,
                **({"from": page} if page is not None else {}),
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            payload = response.json()
            hits = payload.get("hits", [])
            next_page = (
                payload.get("from", None) if payload.get("hasNext", False) else None
            )
            return hits, next_page
        raise TsApi._api_error(response)

    def get_protocols_with_task_script(
        self, *, namespace: str, slug: str, version: str
    ) -> list[dict]:
        """
        :param namespace:
        :param slug:
        :param version:
        :return:
        """
        return self.get_directional_relationships(
            artifact_type="task-scripts",
            namespace=namespace,
            slug=slug,
            version=version,
            other_type="protocols",
        )

    def get_task_scripts_with_ids(
        self, *, namespace: str, slug: str, version: str
    ) -> list[dict]:
        return self.get_directional_relationships(
            artifact_type="ids",
            namespace=namespace,
            slug=slug,
            version=version,
            other_type="task-scripts",
        )

    def get_directional_relationships(
        self,
        *,
        namespace: str,
        slug: str,
        version: str,
        artifact_type: str,
        other_type: str,
    ) -> list[dict]:
        response = requests.get(
            f"{self._api_url}/artifacts/{artifact_type}/{namespace}/{slug}/{version}/relationships",
            **self._request_defaults,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        if response.status_code < 400:
            payload = response.json()
            return payload.get(other_type, [])
        raise TsApi._api_error(response)
