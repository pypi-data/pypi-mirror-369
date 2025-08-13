import asyncio
import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

from httpx import AsyncClient, Client, HTTPError, Response

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from haizelabs.resources._code_of_conduct import (
        AsyncCodeOfConduct,
        SyncCodeOfConduct,
    )
    from haizelabs.resources._datasets import AsyncDatasets, SyncDatasets
    from haizelabs.resources._judges import AsyncJudges, SyncJudges
    from haizelabs.resources._red_team_tests import AsyncRedTeamTests, SyncRedTeamTests
    from haizelabs.resources._unit_tests import AsyncUnitTests, SyncUnitTests

    from .resources._ai_systems import AsyncAISystems, SyncAISystems

log = logging.getLogger(__name__)

API_KEY_HEADER = "X-Haize-API-Key"
BASE_URL = "https://api.haizelabs.com/v1/"

missing_api_key_error = """`HAIZE_API_KEY` not found. Generate an api key at https://platform.haizelabs.com/app/settings
and save as `HAIZE_API_KEY` in your enviornment or pass in to the `api_key` parameter.
"""


class APIClient:
    def __init__(self, api_key: str, base_url: str):
        self.client: Optional[Client] = None
        self.headers = {API_KEY_HEADER: api_key}
        self.base_url = base_url
        self.client = Client(headers=self.headers, base_url=self.base_url)

    def __del__(self) -> None:
        if self.client and not self.client.is_closed:
            self.client.close()

    def close(self) -> None:
        if self.client and not self.client.is_closed:
            self.client.close()

    def get(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.client.get(url, **kwargs)  # type: ignore
        self._raise_for_status(response)
        resp_json: Dict[str, Any] = response.json()
        return resp_json

    def post(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        response = self.client.post(url, **kwargs)  # type: ignore
        self._raise_for_status(response)
        resp_json: Dict[str, Any] = response.json()
        return resp_json

    def delete(self, url: str, **kwargs: Any) -> bool:
        response = self.client.delete(url, **kwargs)  # type: ignore
        self._raise_for_status(response)
        return True

    def _raise_for_status(self, response: Response) -> None:
        message: Optional[str]
        if response.status_code >= 400:
            message = response.text
            raise HTTPError(message=message)


class AsyncAPIClient:
    def __init__(self, api_key: str, base_url: str):
        self.client: Optional[AsyncClient] = None
        self.headers = {API_KEY_HEADER: api_key}
        self.base_url = base_url
        self.client = AsyncClient(
            headers=self.headers, base_url=self.base_url, timeout=100
        )

    def __del__(self) -> None:
        if self.client and self.client.is_closed:
            return
        try:
            asyncio.get_running_loop().create_task(self.close())
        except Exception:
            log.debug("Failed to close async client", exc_info=True)

    async def close(self) -> None:
        if self.client and not self.client.is_closed:
            await self.client.aclose()

    async def get(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        response = await self.client.get(url, **kwargs)
        await self._raise_for_status(response)
        resp_json: Dict[str, Any] = response.json()
        return resp_json

    async def post(self, url: str, **kwargs: Any) -> Dict[str, Any]:
        response = await self.client.post(url, **kwargs)
        await self._raise_for_status(response)
        resp_json: Dict[str, Any] = response.json()
        return resp_json

    async def delete(self, url: str, **kwargs: Any) -> bool:
        response = await self.client.delete(url, **kwargs)
        await self._raise_for_status(response)
        return True

    async def _raise_for_status(self, response: Response) -> None:
        message: Optional[str]
        if response.status_code >= 400:
            message = response.text
            raise HTTPError(message=message)


class Haize(APIClient):
    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        if not api_key and not (api_key := os.environ.get("HAIZE_API_KEY")):
            raise ValueError(missing_api_key_error)
        if not base_url:
            base_url = os.environ.get("HAIZE_BASE_URL", BASE_URL)
        super().__init__(api_key=api_key, base_url=base_url)

    @property
    def ai_systems(self) -> "SyncAISystems":
        from .resources._ai_systems import SyncAISystems

        return SyncAISystems(self)

    @property
    def judges(self) -> "SyncJudges":
        from .resources._judges import SyncJudges

        return SyncJudges(self)

    @property
    def red_team_tests(self) -> "SyncRedTeamTests":
        from .resources._red_team_tests import SyncRedTeamTests

        return SyncRedTeamTests(self)

    @property
    def unit_tests(self) -> "SyncUnitTests":
        from .resources._unit_tests import SyncUnitTests

        return SyncUnitTests(self)

    @property
    def datasets(self) -> "SyncDatasets":
        from .resources._datasets import SyncDatasets

        return SyncDatasets(self)

    @property
    def code_of_conduct(self) -> "SyncCodeOfConduct":
        from .resources._code_of_conduct import SyncCodeOfConduct

        return SyncCodeOfConduct(self)


class AsyncHaize(AsyncAPIClient):
    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        if not api_key and not (api_key := os.environ.get("HAIZE_API_KEY")):
            raise ValueError(missing_api_key_error)
        if not base_url:
            base_url = os.environ.get("HAIZE_BASE_URL", BASE_URL)
        super().__init__(api_key=api_key, base_url=base_url)

    @property
    def ai_systems(self) -> "AsyncAISystems":
        from .resources._ai_systems import AsyncAISystems

        return AsyncAISystems(self)

    @property
    def judges(self) -> "AsyncJudges":
        from .resources._judges import AsyncJudges

        return AsyncJudges(self)

    @property
    def red_team_tests(self) -> "AsyncRedTeamTests":
        from .resources._red_team_tests import AsyncRedTeamTests

        return AsyncRedTeamTests(self)

    @property
    def unit_tests(self) -> "AsyncUnitTests":
        from .resources._unit_tests import AsyncUnitTests

        return AsyncUnitTests(self)

    @property
    def datasets(self) -> "AsyncDatasets":
        from .resources._datasets import AsyncDatasets

        return AsyncDatasets(self)

    @property
    def code_of_conduct(self) -> "AsyncCodeOfConduct":
        from .resources._code_of_conduct import AsyncCodeOfConduct

        return AsyncCodeOfConduct(self)
