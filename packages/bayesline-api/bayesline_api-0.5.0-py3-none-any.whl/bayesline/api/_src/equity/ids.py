import abc
from typing import Literal

import polars as pl

FactorType = Literal["Market", "Style", "Industry", "Region"]


class AssetIdApi:

    @abc.abstractmethod
    def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        """
        Parameters
        ----------
        ids: list[str]
            The ids to lookup.
        top_n: int
            The number of results to return, where `0` denotes all records.

        Returns
        -------
        pl.DataFrame
            a dataframe with all identifiers that could be matched, sorted by
            `id` and `start_date`.
        """
        ...


class AsyncAssetIdApi:

    @abc.abstractmethod
    async def lookup_ids(self, ids: list[str], top_n: int = 0) -> pl.DataFrame:
        """
        Parameters
        ----------
        ids: list[str]
            The ids to lookup.
        top_n: int
            The number of results to return, where `0` denotes all records.

        Returns
        -------
        pl.DataFrame
            a dataframe with all identifiers that could be matched, sorted by
            `id` and `start_date`.
        """
        ...
