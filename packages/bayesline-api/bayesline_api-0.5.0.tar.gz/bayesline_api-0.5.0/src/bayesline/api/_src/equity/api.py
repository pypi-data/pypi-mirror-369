import abc

from bayesline.api._src.equity.calendar import AsyncCalendarLoaderApi, CalendarLoaderApi
from bayesline.api._src.equity.exposure import (
    AsyncExposureLoaderApi,
    ExposureLoaderApi,
)
from bayesline.api._src.equity.ids import (
    AssetIdApi,
    AsyncAssetIdApi,
)
from bayesline.api._src.equity.modelconstruction import (
    AsyncFactorModelConstructionLoaderApi,
    FactorModelConstructionLoaderApi,
)
from bayesline.api._src.equity.portfolio import (
    AsyncPortfolioLoaderApi,
    PortfolioLoaderApi,
)
from bayesline.api._src.equity.portfoliohierarchy import (
    AsyncPortfolioHierarchyLoaderApi,
    PortfolioHierarchyLoaderApi,
)
from bayesline.api._src.equity.portfolioreport import (
    AsyncReportLoaderApi,
    ReportLoaderApi,
)
from bayesline.api._src.equity.riskdataset import (
    AsyncRiskDatasetLoaderApi,
    RiskDatasetLoaderApi,
)
from bayesline.api._src.equity.riskmodels import (
    AsyncFactorModelLoaderApi,
    FactorModelLoaderApi,
)
from bayesline.api._src.equity.universe import (
    AsyncUniverseLoaderApi,
    UniverseLoaderApi,
)
from bayesline.api._src.equity.upload import AsyncUploadersApi, UploadersApi


class BayeslineEquityApi(abc.ABC):

    @property
    @abc.abstractmethod
    def riskdatasets(self) -> RiskDatasetLoaderApi: ...

    @property
    @abc.abstractmethod
    def uploaders(self) -> UploadersApi: ...

    @property
    @abc.abstractmethod
    def ids(self) -> AssetIdApi: ...

    @property
    @abc.abstractmethod
    def calendars(self) -> CalendarLoaderApi: ...

    @property
    @abc.abstractmethod
    def universes(self) -> UniverseLoaderApi: ...

    @property
    @abc.abstractmethod
    def exposures(self) -> ExposureLoaderApi: ...

    @property
    @abc.abstractmethod
    def modelconstruction(self) -> FactorModelConstructionLoaderApi: ...

    @property
    @abc.abstractmethod
    def riskmodels(self) -> FactorModelLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfoliohierarchies(self) -> PortfolioHierarchyLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfolioreport(self) -> ReportLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfolios(self) -> PortfolioLoaderApi: ...


class AsyncBayeslineEquityApi(abc.ABC):

    @property
    @abc.abstractmethod
    def riskdatasets(self) -> AsyncRiskDatasetLoaderApi: ...

    @property
    @abc.abstractmethod
    def uploaders(self) -> AsyncUploadersApi: ...

    @property
    @abc.abstractmethod
    def ids(self) -> AsyncAssetIdApi: ...

    @property
    @abc.abstractmethod
    def calendars(self) -> AsyncCalendarLoaderApi: ...

    @property
    @abc.abstractmethod
    def universes(self) -> AsyncUniverseLoaderApi: ...

    @property
    @abc.abstractmethod
    def exposures(self) -> AsyncExposureLoaderApi: ...

    @property
    @abc.abstractmethod
    def modelconstruction(self) -> AsyncFactorModelConstructionLoaderApi: ...

    @property
    @abc.abstractmethod
    def riskmodels(self) -> AsyncFactorModelLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfoliohierarchies(self) -> AsyncPortfolioHierarchyLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfolioreport(self) -> AsyncReportLoaderApi: ...

    @property
    @abc.abstractmethod
    def portfolios(self) -> AsyncPortfolioLoaderApi: ...
