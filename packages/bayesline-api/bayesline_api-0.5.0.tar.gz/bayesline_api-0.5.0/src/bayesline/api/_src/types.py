import datetime as dt
from typing import Any, Literal, Sequence

import polars as pl
from pydantic import BaseModel

IdType = Literal[
    "bayesid",
    "ticker",
    "composite_figi",
    "cik",
    "cusip8",
    "cusip9",
    "isin",
    "sedol6",
    "sedol7",
    "proxy",
    "name",
]
DNFFilterExpression = tuple[str, str, Any]
DNFFilterExpressions = list[DNFFilterExpression | Sequence[DNFFilterExpression]]

DateLike = str | dt.date | dt.datetime


class DnfFilterExpression(BaseModel):
    column: str
    operator: str
    value: Any


class DnfFilterExpressions(BaseModel):
    filters: list[DnfFilterExpression | list[DnfFilterExpression]]

    def get_columns(self) -> list[str]:
        cols = set()
        for filter in self.filters:
            if isinstance(filter, DnfFilterExpression):
                cols.add(filter.column)
            else:
                for and_filter in filter:
                    cols.add(and_filter.column)
        return list(cols)

    @classmethod
    def from_dnf(cls, dnf: DNFFilterExpressions) -> "DnfFilterExpressions":
        if len(dnf) == 0:
            return cls(filters=[])
        elif isinstance(dnf[0][0], str):
            return cls(
                filters=[
                    DnfFilterExpression(
                        column=filter[0], operator=filter[1], value=filter[2]
                    )
                    for filter in dnf
                ]
            )
        else:
            return cls(
                filters=[
                    [
                        DnfFilterExpression(
                            column=filter[0], operator=filter[1], value=filter[2]
                        )
                        for filter in or_filter
                    ]
                    for or_filter in dnf
                ]
            )

    def to_dnf(self) -> DNFFilterExpressions:
        if len(self.filters) == 0:
            return []

        if isinstance(self.filters[0], DnfFilterExpression):
            return [
                (filter.column, filter.operator, filter.value)  # type: ignore
                for filter in self.filters
            ]
        else:
            return [
                [
                    (and_filter.column, and_filter.operator, and_filter.value)  # type: ignore
                    for and_filter in or_filter
                ]
                for or_filter in self.filters
            ]


def to_date(arg: DateLike) -> dt.date:
    """Cast a date-like object to a date.

    Parameters
    ----------
    arg : DateLike
        The date-like object to cast.

    Returns
    -------
    dt.date
        The date.
    """
    if isinstance(arg, dt.date):
        return arg
    elif isinstance(arg, dt.datetime):
        return arg.date()
    elif isinstance(arg, str):
        try:
            return pl.Series([arg]).str.to_date().to_list()[0]
        except pl.exceptions.ComputeError as e:
            raise ValueError(f"Could not cast string to date: '{arg}'") from e
    else:
        raise ValueError(f"Invalid date-like object: {arg}")


def to_maybe_date(arg: DateLike | None) -> dt.date | None:
    """Cast a date-like object, empty string or None to a date or None.

    Parameters
    ----------
    arg : DateLike | None
        The date-like object to cast.

    Returns
    -------
    dt.date | None
        The date or None.
    """
    if arg is None or arg == "":
        return None
    else:
        return to_date(arg)


def to_date_string(arg: DateLike) -> str:
    """Cast a date-like object to a date string.

    Parameters
    ----------
    arg : DateLike
        The date-like object to cast.

    Returns
    -------
    str
        The date string.
    """
    return to_date(arg).isoformat()


def to_maybe_date_string(arg: DateLike | None) -> str | None:
    """Cast a date-like object, empty string or None to a date string or None.

    Parameters
    ----------
    arg : DateLike | None
        The date-like object to cast.

    Returns
    -------
    str | None
        The date string or None.
    """
    if arg is None or arg == "":
        return None
    else:
        return to_date_string(arg)
