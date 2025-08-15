from typing import Any

from bayesline.api import AsyncUserPermissionsApi, UserPermissionsApi

from bayesline.apiclient._src.apiclient import ApiClient, AsyncApiClient


class AsyncUserPermissionsApiClient(AsyncUserPermissionsApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client

    async def get_permissions_map(self) -> dict[str, Any]:
        response = await self._client.get("/permissions")
        return response.json()

    async def get_perm(self, key: str, default: bool = True) -> Any:
        response = await self._client.get(
            f"/permissions/{key}",
            params={"default": default},
        )
        return response.json()

    async def get_perms(self, keys: list[str], default: bool = True) -> dict[str, Any]:
        response = await self._client.post(
            "/permissions",
            body={"keys": keys, "default": default},
        )
        return response.json()


class UserPermissionsApiClient(UserPermissionsApi):
    def __init__(self, client: ApiClient):
        self._client = client

    def get_permissions_map(self) -> dict[str, Any]:
        response = self._client.get("/permissions")
        return response.json()

    def get_perm(self, key: str, default: bool = True) -> Any:
        response = self._client.get(
            f"/permissions/{key}",
            params={"default": default},
        )
        return response.json()

    def get_perms(self, keys: list[str], default: bool = True) -> dict[str, Any]:
        response = self._client.post(
            "/permissions",
            body={"keys": keys, "default": default},
        )
        return response.json()
