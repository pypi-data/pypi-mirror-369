import base64
import os
import tempfile
from dataclasses import dataclass
from typing import Union
from urllib.parse import urlparse
from uuid import uuid4

import requests

from swarmnode._client import Client
from swarmnode.pagination import PagePaginatedResource
from swarmnode.resources._base import Resource


@dataclass
class AssetStorageRequestResponse:
    request_id: str
    presigned_url: str
    form_data: dict


@dataclass
class Asset(Resource):
    id: str
    name: str
    agent_id: Union[str, None]
    created: str
    url: str

    @classmethod
    def api_source(cls):
        return "assets"

    @classmethod
    def _create_asset_storage_request(
        cls, name: str, agent_id: Union[str, None]
    ) -> AssetStorageRequestResponse:
        r = Client.request_action(
            "POST",
            "asset-storage-requests/create/",
            data={"asset_name": name, "agent_id": agent_id},
        )
        return AssetStorageRequestResponse(**r.json())

    @classmethod
    def _confirm_asset_storage(cls, request_id: str) -> "Asset":
        r = Client.request_action(
            "POST",
            f"{cls.api_source()}/confirm-storage/",
            data={"asset_storage_request_id": request_id},
        )
        return cls(**r.json())

    @classmethod
    def binary_save(
        cls, *, name: str, binary_data: bytes, agent_id: Union[str, None]
    ) -> "Asset":
        p = cls._create_asset_storage_request(name, agent_id)
        response = requests.post(
            p.presigned_url, data=p.form_data, files={"file": binary_data}
        )
        if response.status_code != 204:
            raise Exception(
                f"Failed to upload file: {response.status_code} {response.text}"
            )
        return cls._confirm_asset_storage(p.request_id)

    @classmethod
    def base64_save(
        cls, *, name: str, base64_data: str, agent_id: Union[str, None]
    ) -> "Asset":
        # Remove "data:" prefix if present
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]

        binary_data = base64.b64decode(base64_data)
        return cls.binary_save(name=name, binary_data=binary_data, agent_id=agent_id)

    @classmethod
    def url_save(
        cls,
        *,
        url: str,
        agent_id: Union[str, None],
        name: Union[str, None] = None,
        timeout: int = 30,
        chunk_size: int = 1024 * 1024,
    ) -> "Asset":
        """
        `name` can be used to override the filename of the asset.
        """

        parsed_url = urlparse(url)
        if parsed_url.scheme.lower() not in ("http", "https"):
            raise ValueError("Only http/https URLs are supported.")

        if name is None or name == "":
            # Actual filename of the asset at the URL
            name = os.path.basename(parsed_url.path)
            if not name:
                # Default to a random hex string
                name = uuid4().hex

        tmp_path = None
        try:
            # Stream download to a temp file
            with requests.get(url, stream=True, timeout=timeout) as resp:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                    for chunk in resp.iter_content(chunk_size=chunk_size):
                        if chunk:
                            tmp.write(chunk)

            p = cls._create_asset_storage_request(name, agent_id)

            with open(tmp_path, "rb") as f:
                files = {"file": (name, f)}
                upload_resp = requests.post(
                    p.presigned_url, data=p.form_data, files=files
                )
                if upload_resp.status_code != 204:
                    raise Exception(
                        f"Failed to upload file: {upload_resp.status_code} {upload_resp.text}"
                    )

            return cls._confirm_asset_storage(p.request_id)

        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    @classmethod
    def list(
        cls, *, agent_id: Union[str, None] = None, page: int = 1, page_size: int = 10
    ) -> PagePaginatedResource["Asset"]:
        params = {"page": page, "page_size": page_size, "agent_id": agent_id}
        r = Client.request_action("GET", f"{cls.api_source()}/", params=params)
        return PagePaginatedResource(
            _next_url=r.json()["next"],
            _previous_url=r.json()["previous"],
            _resource_class=cls,
            total_count=r.json()["total_count"],
            current_page=r.json()["current_page"],
            results=[cls(**result) for result in r.json()["results"]],
        )

    @classmethod
    def retrieve(cls, id: str) -> "Asset":
        r = Client.request_action("GET", f"{cls.api_source()}/{id}/")
        return cls(**r.json())
