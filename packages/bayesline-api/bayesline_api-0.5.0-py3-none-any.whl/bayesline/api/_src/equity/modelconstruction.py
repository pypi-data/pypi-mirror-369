import abc

from bayesline.api._src.equity.modelconstruction_settings import (
    ModelConstructionSettings,
    ModelConstructionSettingsMenu,
)
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi


class FactorModelConstructionApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ModelConstructionSettings:
        """
        Returns
        -------
        The modelconstruction settings.
        """
        ...


class AsyncFactorModelConstructionApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> ModelConstructionSettings:
        """
        Returns
        -------
        The modelconstruction settings.
        """
        ...


class FactorModelConstructionLoaderApi(
    RegistryBasedApi[
        ModelConstructionSettings,
        ModelConstructionSettingsMenu,
        FactorModelConstructionApi,
    ],
): ...


class AsyncFactorModelConstructionLoaderApi(
    AsyncRegistryBasedApi[
        ModelConstructionSettings,
        ModelConstructionSettingsMenu,
        AsyncFactorModelConstructionApi,
    ],
): ...
