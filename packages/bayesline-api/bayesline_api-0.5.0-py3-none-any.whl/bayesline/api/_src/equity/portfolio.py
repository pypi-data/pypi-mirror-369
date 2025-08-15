import abc
import datetime as dt
from typing import Literal

import polars as pl

from bayesline.api._src.equity.portfolio_settings import (
    PortfolioOrganizerSettings,
    PortfolioOrganizerSettingsMenu,
    PortfolioSettings,
    PortfolioSettingsMenu,
)
from bayesline.api._src.equity.upload import (
    AsyncDataTypeUploaderApi,
    DataTypeUploaderApi,
)
from bayesline.api._src.registry import (
    AsyncRegistryBasedApi,
    AsyncSettingsRegistry,
    RegistryBasedApi,
    SettingsRegistry,
)
from bayesline.api._src.types import DateLike, IdType


class PortfolioApi(abc.ABC):

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @abc.abstractmethod
    def get_id_types(self) -> dict[str, list[IdType]]:
        """
        Returns
        -------
        dict[str, list[IdType]]:
            The available ID types that at least a portion of assets can be mapped
            to for each portfolio.
        """

    @abc.abstractmethod
    def get_coverage(
        self,
        names: str | list[str] | None = None,
        *,
        by: Literal["date", "asset"] = "date",
        metric: Literal["count", "holding"] = "count",
        stats: list[str] | None = None,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        names: str | list[str], optional
            The names of the portfolios. If not given all portfolios will be calculated.
        by: str, optional
            The coverage aggregation, either by date or by asset.
        metric: str, optional
            The metric to calculate, either count of observations
            or sum of holding values.
        stats: list[str], optional
            list of 'min', 'max', 'mean', collapses `by` into these stats.

        Returns
        -------
        pl.DataFrame:
            The dated coverage count for each id type. `portfolio_group` and
            `portfolio` are the first two columns. If `stats` given, collapses the `by`
            index to the given aggregations.
        """

    @abc.abstractmethod
    def get_portfolio_names(self) -> list[str]: ...

    @abc.abstractmethod
    def get_portfolio_groups(self) -> dict[str, list[str]]: ...

    @abc.abstractmethod
    def get_dates(
        self, names: list[str] | str | None = None, *, collapse: bool = False
    ) -> dict[str, list[dt.date]]: ...

    @abc.abstractmethod
    def get_portfolio(
        self,
        names: list[str] | str,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the portfolios for the given names between given start and end dates.

        Parameters
        ----------
        names: list[str] | str
            The list of portfolio names.
        start_date: DateLike, optional
            The start date of the data to return, inclusive.
        end_date: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            id type to return the portfolio holdings in.

        Returns
        -------
        pl.DataFrame:
            A dataframe with columns `portfolio_group`, `portfolio`, `date`,
            `input_asset_id`, `input_asset_id_type`, `asset_id`, `asset_id_type` and
            `value`.

            If no `id_type` is given then the input ID space will be used unmapped. In
            this case the columns `asset_id`, `asset_id_type` will not be returned.
        """


class AsyncPortfolioApi(abc.ABC):

    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @abc.abstractmethod
    async def get_id_types(self) -> dict[str, list[IdType]]:
        """
        Returns
        -------
        dict[str, list[IdType]]:
            The available ID types that at least a portion of assets can be mapped
            to for each portfolio.
        """

    @abc.abstractmethod
    async def get_coverage(
        self,
        names: str | list[str] | None = None,
        *,
        by: Literal["date", "asset"] = "date",
        metric: Literal["count", "holding"] = "count",
        stats: list[str] | None = None,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        names: str | list[str], optional
            The names of the portfolios. If not given all portfolios will be calculated.
        by: str, optional
            The coverage aggregation, either by date or by asset.
        metric: str, optional
            The metric to calculate, either count of observations
            or sum of holding values.
        stats: list[str], optional
            list of 'min', 'max', 'mean', collapses `by` into these stats.

        Returns
        -------
        pl.DataFrame:
            The dated coverage count for each id type. `portfolio_group` and
            `portfolio` are the first two columns. If `stats` given, collapses the `by`
            index to the given aggregations.
        """

    @abc.abstractmethod
    async def get_portfolio_names(self) -> list[str]: ...

    @abc.abstractmethod
    async def get_portfolio_groups(self) -> dict[str, list[str]]: ...

    @abc.abstractmethod
    async def get_dates(
        self, names: list[str] | str | None = None, *, collapse: bool = False
    ) -> dict[str, list[dt.date]]: ...

    @abc.abstractmethod
    async def get_portfolio(
        self,
        names: list[str] | str,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the portfolios for the given names between given start and end dates.

        Parameters
        ----------
        names: list[str] | str
            The list of portfolio names.
        start_date: DateLike, optional
            The start date of the data to return, inclusive.
        end_date: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            id type to return the portfolio holdings in.

        Returns
        -------
        pl.DataFrame:
            A dataframe with columns `portfolio_group`, `portfolio`, `date`,
            `input_asset_id`, `input_asset_id_type`, `asset_id`, `asset_id_type` and
            `value`.

            If no `id_type` is given then the input ID space will be used unmapped. In
            this case the columns `asset_id`, `asset_id_type` will not be returned.
        """


class PortfolioLoaderApi(
    RegistryBasedApi[
        PortfolioSettings,
        PortfolioSettingsMenu,
        PortfolioApi,
    ]
):
    @property
    @abc.abstractmethod
    def uploader(self) -> DataTypeUploaderApi: ...

    @property
    @abc.abstractmethod
    def organizer_settings(
        self,
    ) -> SettingsRegistry[
        PortfolioOrganizerSettings, PortfolioOrganizerSettingsMenu
    ]: ...


class AsyncPortfolioLoaderApi(
    AsyncRegistryBasedApi[
        PortfolioSettings,
        PortfolioSettingsMenu,
        AsyncPortfolioApi,
    ]
):
    @property
    @abc.abstractmethod
    def uploader(self) -> AsyncDataTypeUploaderApi: ...

    @property
    @abc.abstractmethod
    def organizer_settings(
        self,
    ) -> AsyncSettingsRegistry[
        PortfolioOrganizerSettings, PortfolioOrganizerSettingsMenu
    ]: ...
