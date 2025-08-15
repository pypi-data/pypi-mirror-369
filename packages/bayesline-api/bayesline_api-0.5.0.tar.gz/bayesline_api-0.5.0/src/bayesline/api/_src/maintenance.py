import abc
import datetime
from typing import Any

from pydantic import BaseModel

from bayesline.api._src.types import DateLike


class IncidentSummaryItem(BaseModel):

    datetime: datetime.datetime
    incident_id: str
    source: str


class IncidentSummary(BaseModel):

    items: list[IncidentSummaryItem]

    start_date: datetime.datetime
    end_date: datetime.datetime
    n_start: int
    n_end: int
    n_more: int


class IncidentsServiceApi(abc.ABC):
    """
    Gives access to system incidents such as failed requests, their logs and
    contextual information.
    """

    @abc.abstractmethod
    def submit_incident(
        self, incident_id: str, source: str, body: dict[str, Any]
    ) -> IncidentSummaryItem:
        """
        Submits an incident with the given ID and source.

        Parameters
        ----------
        incident_id : str
            The ID of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-
        source : str
            The source of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-
        body : dict[str, Any]
            The body of the incident.

        Returns
        -------
        IncidentSummaryItem
            The submitted incident item.
        """

    @abc.abstractmethod
    def get_incident_summary(
        self,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        start_idx: int = 0,
        end_idx: int = 999999999,
    ) -> IncidentSummary:
        """
        Obtains incident summaries for the given date and index range.

        Parameters
        ----------
        start_date : DateLike | None, optional
            The start date of the range. If None, the last 24 hours are used.
        end_date : DateLike | None, optional
            The end date of the range. If None, `now` is used.
        start_idx : int, optional
            The start index of the range, `0` being first. Default is 0.
        end_idx : int, optional
            The end index of the range, `-1` being last. Default is 999999999.

        Returns
        -------
        IncidentSummary
            The incident summary.
        """

    @abc.abstractmethod
    def get_incident(self, incident_id: str) -> dict[str, dict[str, Any]]:
        """
        Obtains the incident with the given ID.

        Parameters
        ----------
        incident_id : str
            The ID of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-

        Returns
        -------
        dict
            The incident details.
        """


class AsyncIncidentsServiceApi(abc.ABC):
    """
    Gives access to system incidents such as failed requests, their logs and
    contextual information.
    """

    @abc.abstractmethod
    async def submit_incident(
        self, incident_id: str, source: str, body: dict[str, Any]
    ) -> IncidentSummaryItem:
        """
        Submits an incident with the given ID and source.

        Parameters
        ----------
        incident_id : str
            The ID of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-
        source : str
            The source of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-
        body : dict[str, Any]
            The body of the incident.

        Returns
        -------
        IncidentSummaryItem
            The submitted incident item.
        """

    @abc.abstractmethod
    async def get_incident_summary(
        self,
        start_date: DateLike | None = None,
        end_date: DateLike | None = None,
        start_idx: int = 0,
        end_idx: int = 999999999,
    ) -> IncidentSummary:
        """
        Obtains incident summaries for the given date and index range.

        Parameters
        ----------
        start_date : DateLike | None, optional
            The start date of the range. If None, the last 24 hours are used.
        end_date : DateLike | None, optional
            The end date of the range. If None, `now` is used.
        start_idx : int, optional
            The start index of the range, `0` being first. Default is 0.
        end_idx : int, optional
            The end index of the range, `-1` being last. Default is 999999999.

        Returns
        -------
        IncidentSummary
            The incident summary.
        """

    @abc.abstractmethod
    async def get_incident(self, incident_id: str) -> dict[str, dict[str, Any]]:
        """
        Obtains the incident with the given ID.

        Parameters
        ----------
        incident_id : str
            The ID of the incident.
            Cannot contain any of the following characters: /\\:*?"<>|-

        Returns
        -------
        dict
            The incident details.
        """
