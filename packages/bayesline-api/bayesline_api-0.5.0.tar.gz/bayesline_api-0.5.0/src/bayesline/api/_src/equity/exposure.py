import abc
import datetime as dt
from typing import Literal

import polars as pl

from bayesline.api._src.equity.exposure_settings import (
    ExposureSettings,
    ExposureSettingsMenu,
)
from bayesline.api._src.equity.universe import AsyncUniverseApi, UniverseApi
from bayesline.api._src.equity.universe_settings import UniverseSettings
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.tasks import AsyncTask, Task
from bayesline.api._src.types import DateLike, IdType

FactorType = Literal["Market", "Style", "Industry", "Region"]


class ExposureApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ExposureSettings:
        """
        Returns
        -------
        The settings used to create these exposures.
        """
        ...

    @abc.abstractmethod
    def dates(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        range_only: bool = False,
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | UniverseApi
            The universe to use for the exposure calculation.
        range_only: bool, optional
            If True, returns the first and last date only.

        Returns
        -------
        list of all covered dates.
        """

    @abc.abstractmethod
    def coverage_stats(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | UniverseApi
            The universe to use for the exposure calculation.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        by: str, optional
            The aggregation, either by date or by asset

        Returns
        -------
        pl.DataFrame
            A dataframe with date as the first column, where the remaining columns
            names are the styles and substyles (concatenated with a dot). The values
            are the counts of the underlying data before it was imputed.
        """

    @abc.abstractmethod
    def coverage_stats_as_task(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def get(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | UniverseApi
            The universe to use for the exposure calculation.
        start: DateLike, optional
            The start date of the universe to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        filter_tradedays: bool, default=False
            If True, only returns data for tradedays.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range with a where the date is the first column
            and the asset id is the second column. The remaining columns are the
            individual styles.
        """
        ...

    @abc.abstractmethod
    def get_as_task(
        self,
        universe: str | int | UniverseSettings | UniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> Task[pl.DataFrame]: ...


class AsyncExposureApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ExposureSettings:
        """
        Returns
        -------
        The settings used to create these exposures.
        """
        ...

    @abc.abstractmethod
    async def dates(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        range_only: bool = False,
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | UniverseApi
            The universe to use for the exposure calculation.
        range_only: bool, optional
            If True, returns the first and last date only.

        Returns
        -------
        list of all covered dates.
        """

    @abc.abstractmethod
    async def coverage_stats(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | AsyncUniverseApi
            The universe to use for the exposure calculation.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        by: str, optional
            The aggregation, either by date or by asset

        Returns
        -------
        pl.DataFrame
            A dataframe with date as the first column, where the remaining columns
            names are the styles and substyles (concatenated with a dot). The values
            are the counts of the underlying data before it was imputed.
        """

    @abc.abstractmethod
    async def coverage_stats_as_task(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        id_type: IdType | None = None,
        by: Literal["date", "asset"] = "date",
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def get(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        universe: str | int | UniverseSettings | AsyncUniverseApi
            The universe to use for the exposure calculation.
        start: DateLike, optional
            The start date of the universe to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        filter_tradedays: bool, default=False
            If True, only returns data for tradedays.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range with a where the date is the first column
            and the asset id is the second column. The remaining columns are the
            individual styles.
        """
        ...

    @abc.abstractmethod
    async def get_as_task(
        self,
        universe: str | int | UniverseSettings | AsyncUniverseApi,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        filter_tradedays: bool = False,
    ) -> AsyncTask[pl.DataFrame]: ...


class ExposureLoaderApi(
    RegistryBasedApi[ExposureSettings, ExposureSettingsMenu, ExposureApi],
): ...


class AsyncExposureLoaderApi(
    AsyncRegistryBasedApi[ExposureSettings, ExposureSettingsMenu, AsyncExposureApi],
): ...
