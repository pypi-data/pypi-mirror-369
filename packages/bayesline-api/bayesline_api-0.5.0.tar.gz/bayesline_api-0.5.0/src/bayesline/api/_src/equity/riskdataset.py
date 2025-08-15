import abc
from typing import Literal

from bayesline.api._src.equity.riskdataset_settings import (
    RiskDatasetProperties,
    RiskDatasetSettings,
    RiskDatasetSettingsMenu,
    RiskDatasetUpdateResult,
)
from bayesline.api._src.registry import (
    AsyncRegistryBasedApi,
    RawSettings,
    RegistryBasedApi,
)
from bayesline.api._src.tasks import AsyncTask, Task


class DatasetError(Exception): ...


class RiskDatasetApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> RiskDatasetSettings: ...

    @abc.abstractmethod
    def describe(self) -> RiskDatasetProperties: ...

    @abc.abstractmethod
    def update(self, force: bool = False) -> RiskDatasetUpdateResult:
        """
        Checks the underlying datasets for updates and updates this dataset to
        the latest versions.

        Parameters
        ----------
        force: bool
            If true, the update will be forced even if the dataset is up to date.

        Raises
        ------
        DatasetError
            if an error occurs

        Returns
        -------
        RiskDatasetUpdateResult
            The result of the update operation.
        """

    @abc.abstractmethod
    def update_as_task(self) -> Task[RiskDatasetUpdateResult]: ...


class RiskDatasetLoaderApi(
    RegistryBasedApi[RiskDatasetSettings, RiskDatasetSettingsMenu, RiskDatasetApi],
):

    @abc.abstractmethod
    def get_default_dataset_name(self) -> str:
        """
        Returns
        -------
        str
            The default dataset name that will be populated into settings if no
            dataset name is provided.
        """

    @abc.abstractmethod
    def get_dataset_names(
        self, *, mode: Literal["System", "User", "All"] = "All"
    ) -> list[str]:
        """
        Returns the names of all available datasets.

        Parameters
        ----------
        mode: Literal["System", "User", "All"]
            System: only system wide datasets (available to all users and provided
            by the system).
        User: only user specific datasets (available to the current user).
        All: all datasets (system wide and user specific).

        Returns
        -------
        list[str]
            The names of all available datasets.
        """

    def create_or_replace_dataset(
        self, name: str, settings: RiskDatasetSettings
    ) -> RiskDatasetApi:
        self.delete_dataset_if_exists(name)
        return self.create_dataset(name, settings)

    @abc.abstractmethod
    def create_dataset(
        self, name: str, settings: RiskDatasetSettings
    ) -> RiskDatasetApi:
        """
        Creates a new dataset with the given name and settings.

        Parameters
        ----------
        name : str
            The name of the dataset to create.
        settings : RiskDatasetSettings
            The settings for the dataset to create.

        Raises
        ------
        DatasetError
            if a dataset with the given name already exists
            or if the settings are otherwise invalid

        Returns
        -------
        RiskDatasetApi
            the API of the newly created dataset
        """

    @abc.abstractmethod
    def create_dataset_as_task(
        self, name: str, settings: RiskDatasetSettings
    ) -> Task[RiskDatasetApi]: ...

    @abc.abstractmethod
    def delete_dataset(self, name: str) -> RawSettings:
        """
        Deletes the given dataset.

        Parameters
        ----------
        name : str
            The name of the dataset to delete.

        Raises
        ------
        KeyError
            if the dataset does not exist
        DatasetError
            if the dataset could not be deleted

        Returns
        -------
        RawSettings
            The raw settings of the deleted dataset.
        """

    def delete_dataset_if_exists(self, name: str) -> RawSettings | None:
        """
        Deletes the given dataset if it exists.

        Parameters
        ----------
        name : str
            The name of the dataset to delete.

        Raises
        ------
        DatasetError
            if the dataset could not be deleted

        Returns
        -------
        RawSettings | None
            The raw settings of the deleted dataset if dataset existed.
        """
        if name in self.settings.names():
            return self.delete_dataset(name)
        return None


class AsyncRiskDatasetApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> RiskDatasetSettings: ...

    @abc.abstractmethod
    async def describe(self) -> RiskDatasetProperties: ...

    @abc.abstractmethod
    async def update(self, force: bool = False) -> RiskDatasetUpdateResult:
        """
        Checks the underlying datasets for updates and updates this dataset to
        the latest versions.

        Parameters
        ----------
        force: bool
            If true, the update will be forced even if the dataset is up to date.

        Raises
        ------
        DatasetError
            if an error occurs

        Returns
        -------
        RiskDatasetUpdateResult
            The result of the update operation.
        """

    @abc.abstractmethod
    async def update_as_task(
        self, force: bool = False
    ) -> AsyncTask[RiskDatasetUpdateResult]: ...


class AsyncRiskDatasetLoaderApi(
    AsyncRegistryBasedApi[
        RiskDatasetSettings, RiskDatasetSettingsMenu, AsyncRiskDatasetApi
    ],
):

    @abc.abstractmethod
    async def get_default_dataset_name(self) -> str:
        """
        Returns
        -------
        str
            The default dataset name that will be populated into settings if no
            dataset name is provided.
        """

    @abc.abstractmethod
    async def get_dataset_names(
        self, *, mode: Literal["System", "User", "All"] = "All"
    ) -> list[str]:
        """
        Returns the names of all available datasets.

        Parameters
        ----------
        mode: Literal["System", "User", "All"]
            System: only system wide datasets (available to all users and provided
            by the system).
        User: only user specific datasets (available to the current user).
        All: all datasets (system wide and user specific).

        Returns
        -------
        list[str]
            The names of all available datasets.
        """

    async def create_or_replace_dataset(
        self, name: str, settings: RiskDatasetSettings
    ) -> AsyncRiskDatasetApi:
        await self.delete_dataset_if_exists(name)
        return await self.create_dataset(name, settings)

    @abc.abstractmethod
    async def create_dataset(
        self, name: str, settings: RiskDatasetSettings
    ) -> AsyncRiskDatasetApi:
        """
        Creates a new dataset with the given name and settings.

        Parameters
        ----------
        name : str
            The name of the dataset to create.
        settings : RiskDatasetSettings
            The settings for the dataset to create.

        Raises
        ------
        DatasetError
            if a dataset with the given name already exists
            or if the settings are otherwise invalid

        Returns
        -------
        AsyncRiskDatasetApi
            the API of the newly created dataset
        """

    @abc.abstractmethod
    async def create_dataset_as_task(
        self, name: str, settings: RiskDatasetSettings
    ) -> AsyncTask[AsyncRiskDatasetApi]: ...

    @abc.abstractmethod
    async def delete_dataset(self, name: str) -> RawSettings:
        """
        Deletes the given dataset.

        Parameters
        ----------
        name : str
            The name of the dataset to delete.

        Raises
        ------
        KeyError
            if the dataset does not exist
        DatasetError
            if the dataset could not be deleted

        Returns
        -------
        RawSettings
            The raw settings of the deleted dataset.
        """

    async def delete_dataset_if_exists(self, name: str) -> RawSettings | None:
        """
        Deletes the given dataset if it exists.

        Parameters
        ----------
        name : str
            The name of the dataset to delete.

        Raises
        ------
        DatasetError
            if the dataset could not be deleted

        Returns
        -------
        RawSettings | None
            The raw settings of the deleted dataset if dataset existed.
        """
        if name in await self.settings.names():
            return await self.delete_dataset(name)
        return None
