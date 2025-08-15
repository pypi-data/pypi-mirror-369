import abc
import datetime as dt

from bayesline.api._src.equity.calendar_settings import (
    CalendarSettings,
    CalendarSettingsMenu,
)
from bayesline.api._src.registry import AsyncRegistryBasedApi, RegistryBasedApi
from bayesline.api._src.types import DateLike


class CalendarApi(abc.ABC):

    @property
    @abc.abstractmethod
    def settings(self) -> CalendarSettings:
        """
        Returns
        -------
        The settings used to create this calendar.
        """
        ...

    @abc.abstractmethod
    def get(
        self, *, start: DateLike | None = None, end: DateLike | None = None
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.

        Returns
        -------
        list[dt.date]
            A list of all trade dates this calendar covers, between the start and end
            dates, inclusive, if these are provided.
        """


class AsyncCalendarApi(abc.ABC):
    @property
    @abc.abstractmethod
    def settings(self) -> CalendarSettings:
        """
        Returns
        -------
        The settings used to create this calendar.
        """
        ...

    @abc.abstractmethod
    async def get(
        self, *, start: DateLike | None = None, end: DateLike | None = None
    ) -> list[dt.date]:
        """
        Parameters
        ----------
        start: DateLike, optional
            The start date of the data to return, inclusive.
        end: DateLike, optional
            The end date of the data to return, inclusive.

        Returns
        -------
        list[dt.date]
            A list of all trade dates this calendar covers, between the start and end
            dates, inclusive, if these are provided.
        """


class CalendarLoaderApi(
    RegistryBasedApi[CalendarSettings, CalendarSettingsMenu, CalendarApi],
): ...


class AsyncCalendarLoaderApi(
    AsyncRegistryBasedApi[CalendarSettings, CalendarSettingsMenu, AsyncCalendarApi],
): ...
