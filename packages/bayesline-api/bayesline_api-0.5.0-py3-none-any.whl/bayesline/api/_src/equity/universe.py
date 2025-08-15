import abc
import datetime as dt
from typing import Literal

import polars as pl

from bayesline.api._src.equity.universe_settings import (
    UniverseSettings,
    UniverseSettingsMenu,
)
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.tasks import AsyncTask, Task
from bayesline.api._src.types import DateLike, IdType


class UniverseApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> UniverseSettings:
        """
        Returns
        -------
        The settings used to create this universe.
        """
        ...

    @property
    @abc.abstractmethod
    def id_types(self) -> list[IdType]:
        """
        Returns
        -------
        supported id types for this universe.
        """
        ...

    @abc.abstractmethod
    def coverage(self, id_type: IdType | None = None) -> list[str]:
        """
        Parameters
        ----------
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`

        Raises
        ------
        ValueError
            If the given id type is not supported.

        Returns
        -------
        list of all asset ids this universe covers, in given id type.
        """
        ...

    @abc.abstractmethod
    def coverage_as_task(self, id_type: IdType | None = None) -> Task[list[str]]: ...

    @abc.abstractmethod
    def dates(
        self, *, range_only: bool = False, trade_only: bool = False
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        range_only: bool, default=False
            If True, returns the first and last date only.
        trade_only: bool, default=False
            If True, filter down the dats to trade dates only.

        Returns
        -------
        list of all dates this universe covers.
        """

    @abc.abstractmethod
    def counts(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
        labels: bool = True,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        dates: bool, optional
            If True, groups by dates
        industry_level: int, optional
            The level of industry aggregation to group by.
            0 means no industry aggregation, 1 means level 1, etc.
            Values greater than the max level are treated as the max level.
        region_level: int, optional
            The level of region aggregation to group by.
            0 means no region aggregation, 1 means level 1, etc.
            Values greater than the max level are treated as the max level.
        universe_type: Literal["estimation", "coverage", "both"], optional
            The type of universe to calculate the counts for.
        id_type: IdType, optional
            The id type to calculate the daily stats for, e.g. `ticker`,
            which is relevant as the coverage may differ by id type.
            The given id type must be supported, i.e. in `id_types`.
        labels: bool, optional
            If True, return labels for the counts, otherwise use the codes.

        Returns
        -------
        pl.DataFrame
            Universe counts.
            If grouped by dates then the count will be given.
            If not grouped by dates then the mean/min/max across
            all dates will be given.
        """
        ...

    @abc.abstractmethod
    def counts_as_task(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
        labels: bool = True,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def input_id_mapping(
        self,
        *,
        id_type: IdType | None = None,
        filter_mode: Literal["all", "mapped", "unmapped"] = "all",
        mode: Literal[
            "all", "daily-counts", "input-asset-counts", "latest-name"
        ] = "all",
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`, or the default
            ID type of the universe if `None`.
        filter_mode: Literal[all, mapped, unmapped]
            if `mapped` will only consider assets that could be mapped.
            if `unmapped` will only consider assets that could not be mapped.
        mode: Literal[all, daily-counts, latest-name]
            if `all`, returns all dated mappings
            if `daily-counts`, returns the daily counts of mapped assets
            if `input-asset-counts`, returns the total counts of input assets
            if `latest-name`, returns the latest name of mapped assets

        Returns
        -------
        pl.DataFrame
            If mode is `all`, a DataFrame with `date`, `input_asset_id`,
            `input_asset_id_type`, `output_asset_id`, `output_asset_id_type` and,
            `name` columns.
            It contains contains the original input ID space and the mapped ids.
            The mapped IDs will be `None` if for the given date and input ID the
            asset cannot be mapped.
            If mode is `daily-counts`, a DataFrame with `date` and `count`
            columns.
            If mode is `input-asset-counts`, a DataFrame with `input_asset_id` and `count`
            columns.
            If mode is `latest-name`, a DataFrame with `asset_id` and `name` columns.
        """
        ...

    @abc.abstractmethod
    def get(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        start: DateLike, optional
            The start date of the universe to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported, i.e. in `id_types`.
        filter_tradedays: bool, default=False
            If True, filter down the data to trade dates only.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range.
        """
        ...

    @abc.abstractmethod
    def get_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> Task[pl.DataFrame]: ...


class AsyncUniverseApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> UniverseSettings:
        """
        Returns
        -------
        The settings used to create this universe.
        """
        ...

    @property
    @abc.abstractmethod
    def id_types(self) -> list[IdType]:
        """
        Returns
        -------
        supported id types for this universe.
        """
        ...

    @abc.abstractmethod
    async def coverage(self, id_type: IdType | None = None) -> list[str]:
        """
        Parameters
        ----------
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`

        Raises
        ------
        ValueError
            If the given id type is not supported.

        Returns
        -------
        list of all asset ids this universe covers, in given id type.
        """
        ...

    @abc.abstractmethod
    async def coverage_as_task(
        self, id_type: IdType | None = None
    ) -> AsyncTask[list[str]]: ...

    @abc.abstractmethod
    async def dates(
        self, *, range_only: bool = False, trade_only: bool = False
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        range_only: bool, default=False
            If True, returns the first and last date only.
        trade_only: bool, default=False
            If True, filter down the dats to trade dates only.

        Returns
        -------
        list of all dates this universe covers.
        """

    @abc.abstractmethod
    async def counts(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
        labels: bool = True,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        dates: bool, optional
            If True, groups by dates
        industry_level: int, optional
            The level of industry aggregation to group by.
            0 means no industry aggregation, 1 means level 1, etc.
            Values greater than the max level are treated as the max level.
        region_level: int, optional
            The level of region aggregation to group by.
            0 means no region aggregation, 1 means level 1, etc.
            Values greater than the max level are treated as the max level.
        universe_type: Literal["estimation", "coverage", "both"], optional
            The type of universe to calculate the counts for.
        id_type: IdType, optional
            The id type to calculate the daily stats for, e.g. `ticker`,
            which is relevant as the coverage may differ by id type.
            The given id type must be supported, i.e. in `id_types`.
        labels: bool, optional
            If True, return labels for the counts, otherwise use the codes.

        Returns
        -------
        pl.DataFrame
            Universe counts.
            If grouped by dates then the count will be given.
            If not grouped by dates then the mean/min/max across
            all dates will be given.
        """
        ...

    @abc.abstractmethod
    async def counts_as_task(
        self,
        dates: bool = True,
        industry_level: int = 0,
        region_level: int = 0,
        universe_type: Literal["estimation", "coverage", "both"] = "both",
        id_type: IdType | None = None,
        labels: bool = True,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def input_id_mapping(
        self,
        *,
        id_type: IdType | None = None,
        filter_mode: Literal["all", "mapped", "unmapped"] = "all",
        mode: Literal[
            "all", "daily-counts", "input-asset-counts", "latest-name"
        ] = "all",
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`, or the default
            ID type of the universe if `None`.
        filter_mode: Literal[all, mapped, unmapped]
            if `mapped` will only consider assets that could be mapped.
            if `unmapped` will only consider assets that could not be mapped.
        mode: Literal[all, daily-counts, latest-name]
            if `all`, returns all dated mappings
            if `daily-counts`, returns the daily counts of mapped assets
            if `input-asset-counts`, returns the total counts of input assets
            if `latest-name`, returns the latest name of mapped assets

        Returns
        -------
        pl.DataFrame
            If mode is `all`, a DataFrame with `date`, `input_asset_id`,
            `input_asset_id_type`, `output_asset_id`, `output_asset_id_type` and,
            `name` columns.
            It contains contains the original input ID space and the mapped ids.
            The mapped IDs will be `None` if for the given date and input ID the
            asset cannot be mapped.
            If mode is `daily-counts`, a DataFrame with `date` and `count`
            columns.
            If mode is `input-asset-counts`, a DataFrame with `input_asset_id` and `count`
            columns.
            If mode is `latest-name`, a DataFrame with `asset_id` and `name` columns.
        """
        ...

    @abc.abstractmethod
    async def get(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        start: DateLike, optional
            The start date of the universe to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported, i.e. in `id_types`.
        filter_tradedays: bool, default=False
            If True, filter down the data to trade dates only.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range.
        """
        ...

    @abc.abstractmethod
    async def get_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> AsyncTask[pl.DataFrame]: ...


class UniverseLoaderApi(
    RegistryBasedApi[UniverseSettings, UniverseSettingsMenu, UniverseApi],
): ...


class AsyncUniverseLoaderApi(
    AsyncRegistryBasedApi[UniverseSettings, UniverseSettingsMenu, AsyncUniverseApi],
): ...
