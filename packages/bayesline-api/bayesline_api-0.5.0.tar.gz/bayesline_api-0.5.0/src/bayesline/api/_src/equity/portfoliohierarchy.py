import abc
import datetime as dt

import polars as pl

from bayesline.api._src.equity.portfoliohierarchy_settings import (
    PortfolioHierarchySettings,
    PortfolioHierarchySettingsMenu,
)
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.types import DateLike, IdType


class PortfolioHierarchyApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> PortfolioHierarchySettings:
        """
        Returns
        -------
        The settings used to create this hierarchy.
        """
        ...

    @abc.abstractmethod
    def get_id_types(self) -> dict[str, list[IdType]]:
        """
        Returns
        -------
        dict[str, list[IdType]]:
            The available ID types that at least a portion of assets can be mapped
            to for each portfolio.
            If a portfolio has a benchmark then the available id types are those
            that are available for both the portfolio and the benchmark.
        """

    @abc.abstractmethod
    def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        """
        Parameters
        ----------
        collapse: bool, optional
            If True, will calculate aggregations `any` and `all`, indicating
            of for a given date, any (or all) portfolios have holdings.

        Returns
        -------
        A dict of portfolio-id to dates for which this hierarchy can be produced.
        For a given portfolio and date, the hierarchy can be produced if
        the portfolio has holdings for that date. If a benchmark is given then
        this benchmark also must have holdings for the given date.
        """

    @abc.abstractmethod
    def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame: ...


class AsyncPortfolioHierarchyApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> PortfolioHierarchySettings:
        """
        Returns
        -------
        The settings used to create this hierarchy.
        """
        ...

    @abc.abstractmethod
    async def get_id_types(self) -> dict[str, list[IdType]]:
        """
        Returns
        -------
        dict[str, list[IdType]]:
            The available ID types that at least a portion of assets can be mapped
            to for each portfolio.
            If a portfolio has a benchmark then the available id types are those
            that are available for both the portfolio and the benchmark.
        """

    @abc.abstractmethod
    async def get_dates(self, *, collapse: bool = False) -> dict[str, list[dt.date]]:
        """
        Parameters
        ----------
        collapse: bool, optional
            If True, will calculate aggregations `any` and `all`, indicating
            of for a given date, any (or all) portfolios have holdings.

        Returns
        -------
        A dict of portfolio-id to dates for which this hierarchy can be produced.
        For a given portfolio and date, the hierarchy can be produced if
        the portfolio has holdings for that date. If a benchmark is given then
        this benchmark also must have holdings for the given date.
        """

    @abc.abstractmethod
    async def get(
        self,
        start_date: DateLike | None,
        end_date: DateLike | None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame: ...


class PortfolioHierarchyLoaderApi(
    RegistryBasedApi[
        PortfolioHierarchySettings,
        PortfolioHierarchySettingsMenu,
        PortfolioHierarchyApi,
    ]
): ...


class AsyncPortfolioHierarchyLoaderApi(
    AsyncRegistryBasedApi[
        PortfolioHierarchySettings,
        PortfolioHierarchySettingsMenu,
        AsyncPortfolioHierarchyApi,
    ]
): ...
