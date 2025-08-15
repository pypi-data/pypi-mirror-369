import abc
import datetime as dt
from typing import Literal

import polars as pl

from bayesline.api._src.equity.riskmodels_settings import (
    FactorRiskModelSettings,
    FactorRiskModelSettingsMenu,
)
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.tasks import AsyncTask, Task
from bayesline.api._src.types import DateLike, IdType

FactorType = Literal["Market", "Style", "Industry", "Region", "Other"]


class FactorModelApi(abc.ABC):

    @abc.abstractmethod
    def dates(self) -> list[dt.date]:
        """
        Returns
        -------
        All dates covered by this risk model.
        """
        pass

    @abc.abstractmethod
    def factors(self, *which: FactorType) -> list[str]:
        """
        Parameters
        ----------
        which: FactorType
            The factor types to return, e.g. `Market`, `Style`, `Industry`, `Region`.
            By default returns all factors.

        Returns
        -------
        list of all factors for the given factor types.
        """
        ...

    @abc.abstractmethod
    def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model exposures for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return exposures for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range with the first two column as the date and
            asset id. The remaining columns are the individual styles.
        """
        ...

    @abc.abstractmethod
    def exposures_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model universe for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return universe for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the first column is the date and the
            remaining columns are the asset ids. The values are the universe inclusion.
        """
        ...

    @abc.abstractmethod
    def universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model estimation universe for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return universe for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the first column is the date and the
            remaining columns are the asset ids. The values are the estimation universe
            inclusion.
        """
        ...

    @abc.abstractmethod
    def estimation_universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the exposure-weighted market caps for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the rows are the total market cap
            for each date, weighted by the exposure of each asset. For industry factors,
            this specifically means that the value is the sum of all assets in the
            estimation universe in that industry.
        """
        ...

    @abc.abstractmethod
    def market_caps_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the idiosynchratic volatility weights for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the rows are the idiosyncratic
            volatility for each date.
        """
        ...

    @abc.abstractmethod
    def weights_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the asset returns for this risk model on the next day.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the index is the date
            and the columns are the asset id. The values are the asset returns.
        """
        ...

    @abc.abstractmethod
    def future_asset_returns_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        freq: str, optional
            The frequency of the return aggregation, e.g. `D` for daily.
            Defaults to daily (i.e. unaggregated)
        cumulative: bool, optional
            If True, returns the cumulative returns.
        start: DateLike, optional
        end: DateLike, optional

        Returns
        -------
        pl.DataFrame
            The factor returns for the given date range.
        """
        ...

    @abc.abstractmethod
    def fret_as_task(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def t_stats(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    def t_stats_as_task(self) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def p_values(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    def p_values_as_task(self) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def r2(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    def r2_as_task(self) -> Task[pl.DataFrame]: ...

    @abc.abstractmethod
    def sigma2(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    def sigma2_as_task(self) -> Task[pl.DataFrame]: ...


class AsyncFactorModelApi(abc.ABC):

    @abc.abstractmethod
    async def dates(self) -> list[dt.date]:
        """
        Returns
        -------
        All dates covered by this risk model.
        """
        pass

    @abc.abstractmethod
    async def factors(self, *which: FactorType) -> list[str]:
        """
        Parameters
        ----------
        which: FactorType
            The factor types to return, e.g. `Market`, `Style`, `Industry`, `Region`.
            By default returns all factors.

        Returns
        -------
        list of all factors for the given factor types.
        """
        ...

    @abc.abstractmethod
    async def exposures(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model exposures for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return exposures for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range with the first two column as the date and
            asset id. The remaining columns are the individual styles.
        """
        ...

    @abc.abstractmethod
    async def exposures_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model universe for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return universe for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the first column is the date and the
            remaining columns are the asset ids. The values are the universe inclusion.
        """
        ...

    @abc.abstractmethod
    async def universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def estimation_universe(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> pl.DataFrame:
        """
        Obtains the risk model estimation universe for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.
        stage: int, default=1,
            The stage of the factor model to return universe for, of the potentially
            multi-stage regression. Default to 1 (the first stage).

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the first column is the date and the
            remaining columns are the asset ids. The values are the estimation universe
            inclusion.
        """
        ...

    @abc.abstractmethod
    async def estimation_universe_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
        stage: int = 1,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def market_caps(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the exposure-weighted market caps for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the rows are the total market cap
            for each date, weighted by the exposure of each asset. For industry factors,
            this specifically means that the value is the sum of all assets in the
            estimation universe in that industry.
        """
        ...

    @abc.abstractmethod
    async def market_caps_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def weights(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the idiosynchratic volatility weights for this risk model.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the rows are the idiosyncratic
            volatility for each date.
        """
        ...

    @abc.abstractmethod
    async def weights_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def future_asset_returns(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> pl.DataFrame:
        """
        Obtains the asset returns for this risk model on the next day.

        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.
        id_type: IdType, optional
            The id type to return asset ids in, e.g. `ticker`.
            The given id type must be supported by the linked universe.

        Raises
        ------
        ValueError
            If the given id type is not supported or date range is invalid.

        Returns
        -------
        pl.DataFrame
            The data for the given date range where the index is the date
            and the columns are the asset id. The values are the asset returns.
        """
        ...

    @abc.abstractmethod
    async def future_asset_returns_as_task(
        self,
        *,
        start: DateLike | None = None,
        end: DateLike | None = None,
        id_type: IdType | None = None,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def fret(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> pl.DataFrame:
        """
        Parameters
        ----------
        freq: str, optional
            The frequency of the return aggregation, e.g. `D` for daily.
            Defaults to daily (i.e. unaggregated)
        cumulative: bool, optional
            If True, returns the cumulative returns.
        start: DateLike, optional
        end: DateLike, optional

        Returns
        -------
        pl.DataFrame
            The factor returns for the given date range.
        """
        ...

    @abc.abstractmethod
    async def fret_as_task(
        self,
        *,
        freq: str | None = None,
        cumulative: bool = False,
        start: DateLike | None = None,
        end: DateLike | None = None,
    ) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def t_stats(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    async def t_stats_as_task(self) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def p_values(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    async def p_values_as_task(self) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def r2(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    async def r2_as_task(self) -> AsyncTask[pl.DataFrame]: ...

    @abc.abstractmethod
    async def sigma2(self) -> pl.DataFrame: ...

    @abc.abstractmethod
    async def sigma2_as_task(self) -> AsyncTask[pl.DataFrame]: ...


class FactorModelEngineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> FactorRiskModelSettings:
        """
        Returns
        -------
        The settings used to create these risk model.
        """
        ...

    @abc.abstractmethod
    def get(self) -> FactorModelApi:
        """

        Returns
        -------
        A built `FactorModelApi` instance for given settings.
        """

    @abc.abstractmethod
    def get_as_task(self) -> Task[FactorModelApi]: ...


class AsyncFactorModelEngineApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> FactorRiskModelSettings:
        """
        Returns
        -------
        The settings used to create these risk model.
        """
        ...

    @abc.abstractmethod
    async def get(self) -> AsyncFactorModelApi:
        """

        Returns
        -------
        A built `FactorModelApi` instance for given settings.
        """

    @abc.abstractmethod
    async def get_as_task(self) -> AsyncTask[AsyncFactorModelApi]: ...


class FactorModelLoaderApi(
    RegistryBasedApi[
        FactorRiskModelSettings, FactorRiskModelSettingsMenu, FactorModelEngineApi
    ]
): ...


class AsyncFactorModelLoaderApi(
    AsyncRegistryBasedApi[
        FactorRiskModelSettings, FactorRiskModelSettingsMenu, AsyncFactorModelEngineApi
    ]
): ...
