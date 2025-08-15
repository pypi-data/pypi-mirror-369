import datetime as dt
import io
from typing import Any

import polars as pl
from bayesline.api import (
    AsyncSettingsRegistry,
    SettingsRegistry,
)
from bayesline.api.equity import (
    AssetIdApi,
    AsyncAssetIdApi,
    AsyncBayeslineEquityApi,
    AsyncCalendarLoaderApi,
    AsyncExposureLoaderApi,
    AsyncFactorModelConstructionApi,
    AsyncFactorModelConstructionLoaderApi,
    AsyncFactorModelLoaderApi,
    AsyncPortfolioHierarchyApi,
    AsyncPortfolioHierarchyLoaderApi,
    AsyncPortfolioLoaderApi,
    AsyncReportLoaderApi,
    AsyncRiskDatasetLoaderApi,
    AsyncUniverseLoaderApi,
    AsyncUploadersApi,
    BayeslineEquityApi,
    CalendarLoaderApi,
    ExposureLoaderApi,
    FactorModelConstructionApi,
    FactorModelConstructionLoaderApi,
    FactorModelLoaderApi,
    ModelConstructionSettings,
    ModelConstructionSettingsMenu,
    PortfolioHierarchyApi,
    PortfolioHierarchyLoaderApi,
    PortfolioHierarchySettings,
    PortfolioHierarchySettingsMenu,
    PortfolioLoaderApi,
    ReportLoaderApi,
    RiskDatasetLoaderApi,
    UniverseLoaderApi,
    UploadersApi,
)
from bayesline.api.types import (
    DateLike,
    IdType,
    to_date,
    to_date_string,
)

from bayesline.apiclient._src.client import ApiClient, AsyncApiClient
from bayesline.apiclient._src.equity.calendar import (
    AsyncCalendarLoaderClientImpl,
    CalendarLoaderClientImpl,
)
from bayesline.apiclient._src.equity.dataset import (
    AsyncRiskDatasetLoaderClientImpl,
    RiskDatasetLoaderClientImpl,
)
from bayesline.apiclient._src.equity.exposure import (
    AsyncExposureLoaderClientImpl,
    ExposureLoaderClientImpl,
)
from bayesline.apiclient._src.equity.portfolio import (
    AsyncPortfolioLoaderClientImpl,
    PortfolioLoaderClientImpl,
)
from bayesline.apiclient._src.equity.portfolioreport import (
    AsyncReportLoaderClientImpl,
    ReportLoaderClientImpl,
)
from bayesline.apiclient._src.equity.riskmodels import (
    AsyncFactorModelLoaderClientImpl,
    FactorModelLoaderClientImpl,
)
from bayesline.apiclient._src.equity.universe import (
    AsyncUniverseLoaderClientImpl,
    UniverseLoaderClientImpl,
)
from bayesline.apiclient._src.equity.upload import (
    AsyncUploadersClientImpl,
    UploadersClientImpl,
)
from bayesline.apiclient._src.settings import (
    AsyncHttpSettingsRegistryClient,
    HttpSettingsRegistryClient,
)


class AssetIdClientImpl(AssetIdApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("ids")

    def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        response = self._client.get("lookup", params={"ids": ids, "top_n": top_n})
        try:
            response.raise_for_status()
        except Exception as e:
            raise ValueError(response.json()["detail"]) from e
        return pl.read_parquet(io.BytesIO(response.content))


class AsyncAssetIdClientImpl(AsyncAssetIdApi):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("ids")

    async def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        response = await self._client.get("lookup", params={"ids": ids, "top_n": top_n})
        try:
            response.raise_for_status()
        except Exception as e:
            raise ValueError(response.json()["detail"]) from e
        return pl.read_parquet(io.BytesIO(response.content))


class FactorModelConstructionClientImpl(FactorModelConstructionApi):

    def __init__(
        self,
        client: ApiClient,
        settings: ModelConstructionSettings,
    ):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> ModelConstructionSettings:
        return self._settings


class AsyncFactorModelConstructionClientImpl(AsyncFactorModelConstructionApi):

    def __init__(
        self,
        client: AsyncApiClient,
        settings: ModelConstructionSettings,
    ):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> ModelConstructionSettings:
        return self._settings


class FactorModelConstructionLoaderClientImpl(FactorModelConstructionLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("modelconstruction")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/model-construction"),
            ModelConstructionSettings,
            ModelConstructionSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[ModelConstructionSettings, ModelConstructionSettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | ModelConstructionSettings
    ) -> FactorModelConstructionApi:
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return FactorModelConstructionClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            ref = ref_or_settings
            settings_obj = self.settings.get(ref)
            return FactorModelConstructionClientImpl(self._client, settings_obj)


class AsyncFactorModelConstructionLoaderClientImpl(
    AsyncFactorModelConstructionLoaderApi
):

    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("modelconstruction")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/model-construction"),
            ModelConstructionSettings,
            ModelConstructionSettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[
        ModelConstructionSettings, ModelConstructionSettingsMenu
    ]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | ModelConstructionSettings
    ) -> AsyncFactorModelConstructionApi:
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
        if isinstance(ref_or_settings, ModelConstructionSettings):
            settings = ref_or_settings
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(settings)
            return AsyncFactorModelConstructionClientImpl(self._client, settings)
        else:
            ref = ref_or_settings
            settings_obj = await self.settings.get(ref)
            return AsyncFactorModelConstructionClientImpl(self._client, settings_obj)


class PortfolioHierarchyClientImpl(PortfolioHierarchyApi):

    def __init__(self, client: ApiClient, settings: PortfolioHierarchySettings):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> PortfolioHierarchySettings:
        return self._settings

    def get_id_types(self) -> dict[str, list[IdType]]:
        return self._client.post("id-types", body=self._settings.model_dump()).json()

    def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        response = self._client.post(
            "dates", body=self._settings.model_dump(), params={"collapse": collapse}
        )
        response_data = response.json()
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = to_date_string(start_date)
        if end_date is not None:
            params["end_date"] = to_date_string(end_date)
        if id_type is not None:
            params["id_type"] = id_type
        response = self._client.post(
            "/",
            params=params,
            body=self._settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class AsyncPortfolioHierarchyClientImpl(AsyncPortfolioHierarchyApi):

    def __init__(self, client: AsyncApiClient, settings: PortfolioHierarchySettings):
        self._client = client
        self._settings = settings

    @property
    def settings(self) -> PortfolioHierarchySettings:
        return self._settings

    async def get_id_types(self) -> dict[str, list[IdType]]:
        return (
            await self._client.post("id-types", body=self._settings.model_dump())
        ).json()

    async def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        response = await self._client.post(
            "dates", body=self._settings.model_dump(), params={"collapse": collapse}
        )
        response_data = response.json()
        return {p: [to_date(d) for d in response_data[p]] for p in response_data.keys()}

    async def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        params: dict[str, Any] = {}
        if start_date is not None:
            params["start_date"] = to_date_string(start_date)
        if end_date is not None:
            params["end_date"] = to_date_string(end_date)
        if id_type is not None:
            params["id_type"] = id_type
        response = await self._client.post(
            "/",
            params=params,
            body=self._settings.model_dump(),
        )

        return pl.read_parquet(io.BytesIO(response.content))


class PortfolioHierarchyLoaderClientImpl(PortfolioHierarchyLoaderApi):

    def __init__(self, client: ApiClient):
        self._client = client.append_base_path("portfoliohierarchy")
        self._settings = HttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-hierarchy"),
            PortfolioHierarchySettings,
            PortfolioHierarchySettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> SettingsRegistry[PortfolioHierarchySettings, PortfolioHierarchySettingsMenu]:
        return self._settings

    def load(
        self, ref_or_settings: str | int | PortfolioHierarchySettings
    ) -> PortfolioHierarchyApi:
        if isinstance(ref_or_settings, PortfolioHierarchySettings):
            settings_menu = self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return PortfolioHierarchyClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = self.settings.get(ref_or_settings)
            return PortfolioHierarchyClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )


class AsyncPortfolioHierarchyLoaderClientImpl(AsyncPortfolioHierarchyLoaderApi):
    def __init__(self, client: AsyncApiClient):
        self._client = client.append_base_path("portfoliohierarchy")
        self._settings = AsyncHttpSettingsRegistryClient(
            client.append_base_path("settings/portfolio-hierarchy"),
            PortfolioHierarchySettings,
            PortfolioHierarchySettingsMenu,
        )

    @property
    def settings(
        self,
    ) -> AsyncSettingsRegistry[
        PortfolioHierarchySettings, PortfolioHierarchySettingsMenu
    ]:
        return self._settings

    async def load(
        self, ref_or_settings: str | int | PortfolioHierarchySettings
    ) -> AsyncPortfolioHierarchyApi:
        if isinstance(ref_or_settings, PortfolioHierarchySettings):
            settings_menu = await self._settings.available_settings()
            settings_menu.validate_settings(ref_or_settings)
            return AsyncPortfolioHierarchyClientImpl(self._client, ref_or_settings)
        else:
            portfoliohierarchy_settings = await self.settings.get(ref_or_settings)
            return AsyncPortfolioHierarchyClientImpl(
                self._client,
                portfoliohierarchy_settings,
            )


class BayeslineEquityApiClient(BayeslineEquityApi):
    def __init__(self, client: ApiClient, task_client: ApiClient, tqdm_progress: bool):
        self._client = client.append_base_path("equity")
        self._dataset_client = RiskDatasetLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._uploaders_client = UploadersClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._id_client = AssetIdClientImpl(self._client)
        self._calendar_client = CalendarLoaderClientImpl(self._client)
        self._universe_client = UniverseLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._exposure_client = ExposureLoaderClientImpl(
            self._client, task_client, self._universe_client, tqdm_progress
        )
        self._modelconstruction_client = FactorModelConstructionLoaderClientImpl(
            self._client
        )
        self._factorrisk_client = FactorModelLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._portfoliohierarchy_client = PortfolioHierarchyLoaderClientImpl(
            self._client
        )
        self._portfolioreport_client = ReportLoaderClientImpl(
            self._client,
            task_client,
            self._portfoliohierarchy_client,
            tqdm_progress=tqdm_progress,
        )
        self._portfolio_client = PortfolioLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )

    @property
    def riskdatasets(self) -> RiskDatasetLoaderApi:
        return self._dataset_client

    @property
    def uploaders(self) -> UploadersApi:
        return self._uploaders_client

    @property
    def ids(self) -> AssetIdApi:
        return self._id_client

    @property
    def calendars(self) -> CalendarLoaderApi:
        return self._calendar_client

    @property
    def universes(self) -> UniverseLoaderApi:
        return self._universe_client

    @property
    def exposures(self) -> ExposureLoaderApi:
        return self._exposure_client

    @property
    def modelconstruction(self) -> FactorModelConstructionLoaderApi:
        return self._modelconstruction_client

    @property
    def riskmodels(self) -> FactorModelLoaderApi:
        return self._factorrisk_client

    @property
    def portfolioreport(self) -> ReportLoaderApi:
        return self._portfolioreport_client

    @property
    def portfolios(self) -> PortfolioLoaderApi:
        return self._portfolio_client

    @property
    def portfoliohierarchies(self) -> PortfolioHierarchyLoaderApi:
        return self._portfoliohierarchy_client


class AsyncBayeslineEquityApiClient(AsyncBayeslineEquityApi):

    def __init__(
        self, client: AsyncApiClient, task_client: AsyncApiClient, tqdm_progress: bool
    ):
        self._client = client.append_base_path("equity")
        self._dataset_client = AsyncRiskDatasetLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._uploaders_client = AsyncUploadersClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._id_client = AsyncAssetIdClientImpl(self._client)
        self._calendar_client = AsyncCalendarLoaderClientImpl(self._client)
        self._universe_client = AsyncUniverseLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )

        self._exposure_client = AsyncExposureLoaderClientImpl(
            self._client, task_client, self._universe_client, tqdm_progress
        )
        self._modelconstruction_client = AsyncFactorModelConstructionLoaderClientImpl(
            self._client
        )
        self._factorrisk_client = AsyncFactorModelLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )
        self._portfoliohierarchy_client = AsyncPortfolioHierarchyLoaderClientImpl(
            self._client
        )
        self._portfolioreport_client = AsyncReportLoaderClientImpl(
            self._client,
            task_client,
            self._portfoliohierarchy_client,
            tqdm_progress=tqdm_progress,
        )
        self._portfolio_client = AsyncPortfolioLoaderClientImpl(
            self._client, task_client, tqdm_progress
        )

    @property
    def riskdatasets(self) -> AsyncRiskDatasetLoaderApi:
        return self._dataset_client

    @property
    def uploaders(self) -> AsyncUploadersApi:
        return self._uploaders_client

    @property
    def ids(self) -> AsyncAssetIdApi:
        return self._id_client

    @property
    def calendars(self) -> AsyncCalendarLoaderApi:
        return self._calendar_client

    @property
    def universes(self) -> AsyncUniverseLoaderApi:
        return self._universe_client

    @property
    def exposures(self) -> AsyncExposureLoaderApi:
        return self._exposure_client

    @property
    def modelconstruction(self) -> AsyncFactorModelConstructionLoaderApi:
        return self._modelconstruction_client

    @property
    def riskmodels(self) -> AsyncFactorModelLoaderApi:
        return self._factorrisk_client

    @property
    def portfolioreport(self) -> AsyncReportLoaderApi:
        return self._portfolioreport_client

    @property
    def portfolios(self) -> AsyncPortfolioLoaderApi:
        return self._portfolio_client

    @property
    def portfoliohierarchies(self) -> AsyncPortfolioHierarchyLoaderApi:
        return self._portfoliohierarchy_client
