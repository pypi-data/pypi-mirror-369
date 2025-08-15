import datetime
import json
import os
from collections.abc import Mapping
from typing import Annotated, Any, Literal

import polars as pl
from pydantic import AfterValidator, BaseModel, Field, field_validator, model_validator

from bayesline.api._src.equity import settings as settings_tools
from bayesline.api._src.equity.calendar_settings import (
    CalendarSettings,
    CalendarSettingsMenu,
    require_sorted_unique,
)
from bayesline.api._src.registry import Settings, SettingsMenu
from bayesline.api._src.types import IdType

Hierarchy = settings_tools.Hierarchy


class IndustrySettings(BaseModel, frozen=True, extra="forbid"):
    """
    Specifies include and exclude filters for industries.

    Assets are includes if they are part of at least one include
    and not part of any exclude.

    By default all industries for the given hierarchy are included.
    """

    hierarchy: str = Field(
        default="trbc",
        min_length=1,
        description="The industry hierarchy to use.",
        examples=["trbc"],
    )

    include: list[str] | Literal["All"] = Field(
        default="All",
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the highest "
            "level is used."
        ),
        examples=[["3571"], "All", ["Materials", "1010"]],
    )

    exclude: list[str] = Field(
        default_factory=list,
        description=(
            "Valid industry codes or labels for given hierarchy at any level. If "
            "labels are used which may be duplicated, then the code with the lowest "
            "level is used."
        ),
        examples=[["3571"], ["Materials", "1010"]],
    )


class RegionSettings(BaseModel, frozen=True, extra="forbid"):
    """
    Specifies include and exclude filters for countries and regions.

    Assets are includes if they are part of at least one include
    and not part of any exclude.

    By default all countries for the given hierarchy are included.
    """

    hierarchy: str = Field(
        default="continent",
        min_length=1,
        description="The region hierarchy to use.",
        examples=["continent"],
    )

    include: list[str] | Literal["All"] = Field(
        default="All",
        description=(
            "Valid country/region codes or labels at any level. If labels are used "
            "which may be duplicated, then the code with the highest level is used."
        ),
        examples=[["Europe", "CAN"], "All"],
    )

    exclude: list[str] = Field(
        default_factory=list,
        description=(
            "Valid country/region codes or labels at any level. If labels are used "
            "which may be duplicated, then the code with the lowest level is used."
        ),
        examples=[["DEU"]],
    )


class MCapSettings(BaseModel, frozen=True, extra="forbid"):
    """
    Specifies the lower and upper bound for the market cap filter.

    By default the bounds are infinite.
    """

    lower: float = Field(
        default=0.0,
        ge=0.0,
        description="Lower bound of the cap filter in USD.",
        examples=[1e10],
    )

    upper: float = Field(
        default=1e20,
        gt=0.0,
        description="Upper bound of the cap filter in USD.",
        examples=[1e12],
    )

    gdp_deflator_asof: datetime.date | None = Field(
        default=None,
        description="""
        The as of date to adjust the market cap bounds for GDP through time.
        If no date is specified then the market cap bounds are static through time.
        """,
    )

    @model_validator(mode="after")
    def check_upper_gt_lower(self) -> "MCapSettings":
        if (lower := self.lower) >= (upper := self.upper):
            raise ValueError(
                f"upper bound {upper} must be greater than lower bound {lower}",
            )
        else:
            return self


class UniverseSettings(Settings):
    """
    Defines an asset universe as a set of regional, industry and market cap filters.
    """

    @classmethod
    def default(cls: type["UniverseSettings"]) -> "UniverseSettings":
        """
        Creates default universe settings with no filters and
        cusip as the default id type.
        """
        return cls()

    dataset: str | None = Field(
        default=None,
        description=(
            "The name of the underlying dataset to use. If none is given then the "
            "configured default dataset is used."
        ),
        examples=["Bayesline-US"],
    )

    id_type: IdType = Field(
        default="bayesid",
        description="The default id type to use for the universe.",
        examples=["cusip9", "bayesid"],
    )

    calendar: CalendarSettings = Field(
        default_factory=CalendarSettings,
        description="The calendar settings to use for the universe.",
    )

    industry: IndustrySettings = Field(
        default_factory=IndustrySettings,
        description="""
        Filters that determine which industries to include and exclude in the universe.
        """,
    )

    region: RegionSettings = Field(
        default_factory=RegionSettings,
        description="""
        Filters that determine which countries/continents to include and exclude in the
        universe.
        """,
    )

    mcap: MCapSettings = Field(
        default_factory=MCapSettings,
        description="""
        Filters that determine which market caps to include and exclude in the universe.
        """,
    )

    @model_validator(mode="before")
    @classmethod
    def propagate_dataset(cls: type["UniverseSettings"], data: Any) -> Any:
        """
        Propagates the dataset to the calendar.
        """
        if isinstance(data, dict) and "dataset" in data:
            if "calendar" not in data:
                data["calendar"] = {}
            if isinstance(data["calendar"], dict):
                if data["calendar"].get("dataset") is None:
                    data["calendar"]["dataset"] = data["dataset"]
        return data


class UniverseSettingsMenu(SettingsMenu, frozen=True, extra="forbid"):
    """
    Contains the available settings that can be used for the universe settings.
    """

    id_types: list[IdType] = Field(
        description="""
        A list of all the id types that are supported for the universe.
        """,
    )

    exchanges: Annotated[list[str], AfterValidator(require_sorted_unique)] = Field(
        description="""
        A list of mic codes of all exchanges. Must be sorted and unique.
        """,
    )

    industry: Mapping[str, Mapping[str, Hierarchy]] = Field(
        description="""
        A dictionary where the key is the name of the industry hierarchy (e.g. 'GICS')
        and the value is a N-level nested dictionary structure of the industry hierarchy
        codes.
        """,
    )

    region: Mapping[str, Mapping[str, Hierarchy]] = Field(
        description="""
        A dictionary where the key is the name of the region hierarchy (e.g.
        'CONTINENT') and the value is a N-level nested dictionary structure of the
        region hierarchy codes.
        """,
    )

    industry_labels: Mapping[str, Mapping[str, str]] = Field(
        description="""
        A dictionary where the key is the name of the industry hierarchy and
        the value is a mapping from unique industry code to a human readable name.
        """,
    )

    region_labels: Mapping[str, Mapping[str, str]] = Field(
        description="""
        A dictionary where the key is the name of the region hierarchy and
        the value is a mapping from unique region code to a human readable name.
        """,
    )

    def describe(self, settings: UniverseSettings | None = None) -> str:
        industry = self.industry
        region = self.region

        if settings is not None:
            self.validate_settings(settings)

            industry_hierarchy_name = settings.industry.hierarchy
            effective_industries = set(self.effective_industries(settings.industry))
            effective_industry_hierarchy = settings_tools.map_hierarchy(
                settings_tools.filter_leaves(
                    self.industry[industry_hierarchy_name],
                    lambda k: k in effective_industries,
                ),
                self.industry_labels[industry_hierarchy_name].__getitem__,
            )

            region_hierarchy_name = settings.region.hierarchy
            effective_regions = self.effective_regions(settings.region)
            effective_region_hierarchy = settings_tools.map_hierarchy(
                settings_tools.filter_leaves(
                    self.region[region_hierarchy_name],
                    lambda k: k in effective_regions,
                ),
                self.region_labels[region_hierarchy_name].__getitem__,
            )

            description = [
                f"Default ID Type: {settings.id_type!r}",
                f"Industry Hierarchy ({industry_hierarchy_name}):",
                json.dumps(effective_industry_hierarchy, indent=2),
                f"Region Hierarchy ({region_hierarchy_name}):",
                json.dumps(effective_region_hierarchy, indent=2),
                "Market Cap:",
                settings.mcap.model_dump_json(indent=2),
            ]
        else:
            industry_strs = []
            region_strs = []
            for hierarchy in industry:
                industry_str = json.dumps(
                    {
                        hierarchy: settings_tools.map_hierarchy(
                            industry[hierarchy],
                            self.industry_labels[hierarchy].__getitem__,
                        ),
                    },
                    indent=2,
                )
                industry_strs.append(industry_str)

            for hierarchy in region:
                region_str = json.dumps(
                    {
                        hierarchy: settings_tools.map_hierarchy(
                            region[hierarchy],
                            self.region_labels[hierarchy].__getitem__,
                        ),
                    },
                    indent=2,
                )
                region_strs.append(region_str)

            id_types = ", ".join(self.id_types)
            description = [
                f"ID Types: {id_types}",
                "Industry Hierarchies:",
                os.linesep.join(industry_strs),
                "Region Hierarchies:",
                os.linesep.join(region_strs),
            ]

        return os.linesep.join(description)

    @field_validator("industry", "region")
    @classmethod
    def check_unique_hierarchy(
        cls: type["UniverseSettingsMenu"],
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        return settings_tools.check_unique_hierarchy(v)

    @field_validator("industry", "region")
    @classmethod
    def check_nonempty_hierarchy(
        cls: type["UniverseSettingsMenu"],
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        return settings_tools.check_nonempty_hierarchy(v)

    @model_validator(mode="after")
    def check_all_codes_have_labels(self) -> "UniverseSettingsMenu":
        industry_errors = settings_tools.check_all_codes_have_labels(
            self.industry,
            self.industry_labels,
        )
        region_errors = settings_tools.check_all_codes_have_labels(
            self.region,
            self.region_labels,
        )

        errors = industry_errors + region_errors
        if errors:
            raise ValueError(os.linesep.join(errors))
        else:
            return self

    def effective_industries(
        self,
        settings: IndustrySettings,
        labels: bool = False,
    ) -> list[str]:
        """
        Parameters
        ----------
        settings: IndustrySettings
                  the industry settings to get the effective industries for.

        labels: bool
                whether to return the labels or the codes.

        Returns
        -------
        The effective leaf level industries for the given settings after the filters
        were applied.
        """
        self.validate_industry(settings)
        hierarchy = self.industry[settings.hierarchy]
        includes = settings.include
        excludes = settings.exclude
        industry_labels = self.industry_labels[settings.hierarchy]
        effective_codes = self.get_effective_includes(
            hierarchy,
            includes,
            excludes,
            industry_labels,
        )
        if labels:
            return [industry_labels[code] for code in effective_codes]
        else:
            return effective_codes

    def effective_regions(
        self,
        settings: RegionSettings,
        labels: bool = False,
    ) -> list[str]:
        """
        Parameters
        ----------
        settings: RegionSettings
                  the region settings to get the effective regions for.

        labels: bool
                whether to return the labels or the codes.

        Returns
        -------
        The effective leaf level regions for the given settings after the filters were
        applied.
        """
        self.validate_region(settings)
        hierarchy = self.region[settings.hierarchy]
        includes = settings.include
        excludes = settings.exclude
        region_labels = self.region_labels[settings.hierarchy]
        effective_codes = self.get_effective_includes(
            hierarchy,
            includes,
            excludes,
            region_labels,
        )
        if labels:
            return [region_labels[code] for code in effective_codes]
        else:
            return effective_codes

    def validate_settings(self, settings: UniverseSettings) -> None:
        """
        Validates the given universe settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: UniverseSettings
                  the universe settings to validate against.
        """
        if settings.id_type not in self.id_types:
            raise ValueError(
                f"""
                Id type {settings.id_type} does not exist.
                Only {', '.join(self.id_types)} exist.
                """,
            )
        self.validate_calendar(settings.calendar)
        self.validate_industry(settings.industry)
        self.validate_region(settings.region)

    def validate_calendar(self, settings: CalendarSettings) -> None:
        """
        Validates the given calendar settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: CalendarSettings
                  the calendar settings to validate against.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        CalendarSettingsMenu._validate_exchanges(self.exchanges, settings)

    def validate_industry(self, settings: IndustrySettings) -> None:
        """
        Validates the given industry settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: IndustrySettings
                  the industry settings to validate against.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        available_settings = self.industry
        settings_tools.validate_hierarchy_schema(
            available_settings.keys(),
            settings.hierarchy,
        )
        self._validate_hierarchy(
            available_settings[settings.hierarchy],
            settings.include,
            settings.exclude,
            self.industry_labels[settings.hierarchy],
        )

    def validate_region(self, settings: RegionSettings) -> None:
        """
        Validates the given region settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: RegionSettings
                  the region settings to validate against.
        """
        if settings is None:
            raise ValueError("settings cannot be None")

        available_settings = self.region
        settings_tools.validate_hierarchy_schema(
            available_settings.keys(),
            settings.hierarchy,
        )
        self._validate_hierarchy(
            available_settings[settings.hierarchy],
            settings.include,
            settings.exclude,
            self.region_labels[settings.hierarchy],
        )

    @staticmethod
    def _validate_hierarchy(
        hierarchy: Mapping[str, Hierarchy],
        includes: list[str] | Literal["All"],
        excludes: list[str],
        labels: Mapping[str, str],
    ) -> None:
        flat_hierarchy = settings_tools.flatten(hierarchy)
        label_values = set(labels.values())

        unknown = []
        if includes != "All":
            unknown.extend(
                [
                    include
                    for include in includes
                    if include not in flat_hierarchy and include not in label_values
                ],
            )

        unknown.extend(
            [
                exclude
                for exclude in excludes
                if exclude not in flat_hierarchy and exclude not in label_values
            ],
        )

        if len(unknown) > 0:
            raise ValueError(f"there are unknown items: {', '.join(unknown)}")

        effective_includes = UniverseSettingsMenu.get_effective_includes(
            hierarchy,
            includes,
            excludes,
            labels,
        )
        if len(effective_includes) == 0:
            raise ValueError(
                "the includes and exclude statements lead to an empty set.",
            )

    @staticmethod
    def get_effective_includes(  # noqa: C901
        hierarchy: Mapping[str, Hierarchy],
        includes: list[str] | Literal["All"],
        excludes: list[str],
        labels: Mapping[str, str],
    ) -> list[str]:
        leaf_includes = []
        if isinstance(includes, str) and includes == "All":
            leaf_includes = settings_tools.flatten(hierarchy, only_leaves=True)
        else:
            for include in includes:
                v = settings_tools.find_in_hierarchy(hierarchy, include)
                if v is None:
                    # must be a label then
                    codes = [k for k, v in labels.items() if v == include]
                    if not codes:
                        raise AssertionError(
                            f"{v} is unknown which at this stage should've been verified"
                        )

                    # find the highest level in the hierarchy for possible codes
                    depths = {
                        settings_tools.find_in_hierarchy(
                            hierarchy,
                            code,
                            return_depth=True,
                        ): code
                        for code in codes
                    }
                    if len(depths) != len(codes):
                        raise AssertionError(
                            f"Include {include}: {codes} - {depths}"
                            "illegal, all codes must be represented"
                        )
                    v = settings_tools.find_in_hierarchy(
                        hierarchy,
                        depths[min(depths.keys())],  # type: ignore
                    )

                if isinstance(v, list):
                    leaf_includes.extend(v)
                else:
                    if not isinstance(v, Mapping):
                        raise AssertionError()
                    leaf_includes.extend(
                        settings_tools.flatten(v, only_leaves=True),
                    )

        leaf_excludes = []
        for exclude in excludes:
            v = settings_tools.find_in_hierarchy(hierarchy, exclude)
            if v is None:
                # must be a label then
                codes = [k for k, v in labels.items() if v == exclude]
                if not codes:
                    raise AssertionError(
                        f"{v} is unknown which at this stage should've been verified"
                    )

                # find the lowest level in the hierarchy for possible codes
                depths = {
                    settings_tools.find_in_hierarchy(
                        hierarchy,
                        code,
                        return_depth=True,
                    ): code
                    for code in codes
                }
                v = settings_tools.find_in_hierarchy(
                    hierarchy,
                    depths[max(depths.keys())],  # type: ignore
                )

            if isinstance(v, list):
                leaf_excludes.extend(v)
            else:
                if not isinstance(v, Mapping):
                    raise AssertionError()
                leaf_excludes.extend(settings_tools.flatten(v, only_leaves=True))

        return list(set(leaf_includes) - set(leaf_excludes))

    def industry_hierarchy_df(self, hierarchy: str) -> pl.DataFrame:
        """
        Returns a dataframe of the given industry hierarchy.

        Parameters
        ----------
        hierarchy: str
            the name of the industry hierarchy to return.

        Returns
        -------
        A dataframe of the given industry hierarchy. The uneven levels are filled with
        the codes, and the even ones are filled with the corresponding labels.
        """
        return settings_tools.hierarchy_df_to_wide(
            self.industry[hierarchy], self.industry_labels[hierarchy]
        )

    def region_hierarchy_df(self, hierarchy: str) -> pl.DataFrame:
        """
        Returns a dataframe of the given region hierarchy.

        Parameters
        ----------
        hierarchy: str
            the name of the region hierarchy to return.

        Returns
        -------
        A dataframe of the given region hierarchy. The uneven levels are filled with
        the codes, and the even ones are filled with the corresponding labels.
        """
        return settings_tools.hierarchy_df_to_wide(
            self.region[hierarchy], self.region_labels[hierarchy]
        )
