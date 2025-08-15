from typing import Annotated, Any

from pydantic import AfterValidator, Field

from bayesline.api._src.registry import Settings, SettingsMenu


class CalendarSettings(Settings):
    """
    Defines the settings for the calendar.
    """

    dataset: str | None = Field(
        default=None,
        description=(
            "The name of the underlying dataset to use. If none is given then the "
            "configured default dataset is used."
        ),
        examples=["Bayesline-US"],
    )

    filters: list[list[str]] = Field(
        default=[["XNYS"]],
        min_length=1,
        description=(
            "The filters to apply. Each filter is a list of exchange MIC codes. The "
            "outer list will be treated as an OR conditions, while the inner lists "
            "will be treated as an AND conditions. For example, `[['A', 'B'], ['C']]` "
            "means that the holidays are the days where either A and B are both "
            "holidays, or C is a holiday."
        ),
        examples=[[["XNYS"]], [["XNYS", "XNAS"]], [["XNYS"], ["XNAS"]]],
    )

    @classmethod
    def default(cls: type["CalendarSettings"]) -> "CalendarSettings":
        """
        Creates default calendar settings with just the XNYS exchange as a filter.
        """
        return cls()


def require_sorted_unique(v: Any) -> Any:
    """
    Validates that the given list is sorted and unique.

    Parameters
    ----------
    v: list[Any]
       The list to validate.

    Returns
    -------
    list[Any]
        The validated list.
    """
    if len(v) != len(set(v)):
        raise ValueError("The list must be unique.")
    if v != sorted(v):
        raise ValueError("The list must be sorted.")
    return v


class CalendarSettingsMenu(SettingsMenu, frozen=True, extra="forbid"):
    """
    Contains the available settings that can be used for the calendar settings.
    """

    exchanges: Annotated[list[str], AfterValidator(require_sorted_unique)] = Field(
        description="""
        A list of mic codes of all exchanges. Must be sorted and unique.
        """,
    )

    def describe(self, settings: CalendarSettings | None = None) -> str:
        if settings is not None:
            self.validate_settings(settings)
            # TODO: add a description for the settings
        else:
            # TODO: add a description for the menu
            pass

        raise NotImplementedError()

    @staticmethod
    def _validate_exchanges(exchanges: list[str], settings: CalendarSettings) -> None:
        not_found = []
        for filter_or in settings.filters:
            for filter_and in filter_or:
                if filter_and not in exchanges:
                    not_found.append(filter_and)

        if not_found:
            raise ValueError(
                f"""
                The following exchanges do not exist: {', '.join(not_found)}.
                Only {', '.join(exchanges)} exist.
                """,
            )

    def validate_settings(self, settings: CalendarSettings) -> None:
        """
        Validates the given calendar settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: CalendarSettings
                  the calendar settings to validate against.
        """
        self._validate_exchanges(self.exchanges, settings)
