import json
import os
from collections import Counter
from collections.abc import Mapping
from typing import Literal

import polars as pl
from pydantic import BaseModel, Field, field_validator, model_validator

from bayesline.api._src.equity import settings as settings_tools
from bayesline.api._src.equity.universe_settings import (
    IndustrySettings,
    RegionSettings,
    UniverseSettings,
    UniverseSettingsMenu,
)
from bayesline.api._src.registry import Settings, SettingsMenu

Hierarchy = settings_tools.Hierarchy

# flake8: noqa: E800


class HierarchyDescription(BaseModel):

    hierarchy: str = Field(
        min_length=1,
        description="""
        The name of the hierarchy to use, e.g. 'trbc' or 'continent'.
        If it is not given then the default hierarchy will be used.
        """,
        examples=["trbc", "continent"],
    )


class HierarchyLevel(HierarchyDescription):
    """
    The hierarchy level description turns every name at
    the configured level into a separate factor.

    E.g. for industries specifying level `1` would
    create top level sector factors.
    """

    level: int = Field(
        description="""The level of the hierarchy to use, e.g. 1
        to use all level 1 names (i.e. sectors for industries or
        continents for regions) or 2 to use all level 2
        names (i.e. sub-sectors for industries and
        countries for regions).
        """,
        default=1,
        examples=[1, 2],
        ge=1,
    )


class HierarchyGroups(HierarchyDescription):
    """
    The hierarchy group description allows for a nested definition
    of groupings.
    The top level groupings will turn into factors, whereas any nested
    groupings will be retained for other uses (e.g. risk decomposition).
    """

    groupings: Mapping[str, Hierarchy] = Field(
        description="""
        A nested structure of groupings where the keys are the group names
        and the leaf level is a list of hierarchy codes or labels (at any level)
        to include for this group.
        """,
    )


class ExposureSettings(Settings):
    """
    Defines exposures as hierarchy of selected styles and substyles.
    """

    @classmethod
    def default(cls: type["ExposureSettings"]) -> "ExposureSettings":
        return cls()

    market: bool = Field(
        default=True,
        description="""
        Whether to include the market factor in the model.
        """,
    )

    styles: Mapping[str, list[str]] | None = Field(
        default=None,
        description="""
        A mapping where the keys are style codes or labels and the values are
        lists of included sub-style names or labels.
        By default (None) the entire available style/substyle hierarchy will be used.
        Passing an empty dict will exclude all styles.
        """,
    )
    standardize_styles: bool = Field(
        description="Whether to standardize the style exposures.",
        default=True,
    )

    industries: HierarchyLevel | HierarchyGroups | None = Field(
        description="""
        The definition of how industry factors are being constructed.
        The default is to use the same hiearchy as was used to define the universe
        at level 1 (i.e. coarse grouping).
        None indicates that no industry factors should be included.
        """,
        default_factory=lambda: HierarchyLevel(hierarchy="trbc", level=1),
    )

    regions: HierarchyLevel | HierarchyGroups | None = Field(
        description="""
        The definition of how region factors are being constructed.
        The default is to use the same hiearchy as was used to define the universe
        at level 2 (i.e. granular grouping).
        None indicates that no region factors should be included.
        """,
        default_factory=lambda: HierarchyLevel(hierarchy="continent", level=2),
    )

    other: Mapping[str, str] = Field(
        description="""
        A mapping of other factors to include in the model, to the exposure names or
        labels. For example, to include the risk free rate as an exposure, the mapping
        could be `{"Risk Free Rate": "us_rate_3m"}`, or 
        `{"Risk-Free-Rate": "3 Month US TBill Rate"}`, the key being the exposure name 
        in the output.
        """,
        default_factory=lambda: {},
    )


class ExposureSettingsMenu(SettingsMenu[ExposureSettings], frozen=True, extra="forbid"):
    """
    Contains the available settings that can be used to define exposures.
    """

    market: str = Field(
        description="""
        The unique market factor code to use in the model.
        """,
    )

    styles: Mapping[str, list[str]] = Field(
        description="""
        A mapping where the key is the name of an exposure style codes (e.g. 'LEVERAGE')
        and the value is a list of available sub-style codes (e.g. 'DEBT_TO_ASSETS')
        """,
    )

    industries: Mapping[str, Mapping[str, Hierarchy]] = Field(
        description="""
        A dictionary where the key is the name of the industry hierarchy (e.g. 'TRBC')
        and the value is a N-level nested dictionary structure of the industry hierarchy
        codes.
        """,
    )

    regions: Mapping[str, Mapping[str, Hierarchy]] = Field(
        description="""
        A dictionary where the key is the name of the region hierarchy (e.g.
        'CONTINENT') and the value is a N-level nested dictionary structure of the
        region hierarchy codes.
        """,
    )

    other: set[str] = Field(
        description="""
        A set of other factor codes that can be included in the model.
        """,
    )

    market_labels: Mapping[str, str] = Field(
        description="""
        A mapping from unique market factor code to a human readable name. This is just 
        one pair, but the name is `market_labels` to be consistent.
        """,
        min_length=1,
        max_length=1,
    )

    style_labels: Mapping[str, str] = Field(
        description="""
        A mapping from unique style/substyle code to a human readable name.
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

    other_labels: Mapping[str, str] = Field(
        description="""
        A mapping from unique other factor code to a human readable name.
        """,
    )

    def effective_industry_hierarchy(
        self,
        filter_settings: IndustrySettings,
        settings: HierarchyLevel | HierarchyGroups | None,
    ) -> Mapping[str, Hierarchy]:
        """
        Parameters
        ----------
        filter_settings: IndustrySettings
                    the settings to use to filter the universe.
        settings: HierarchyLevel | HierarchyGroups | None
                  the settings to use to determine the industry factors.

        Returns
        -------
        A dict structure where the keys are the industry factor names
        and the values are the industry codes that are included in that factor.
        """
        if not settings:
            return {}

        effective_includes = UniverseSettingsMenu.get_effective_includes(
            self.industries[settings.hierarchy],
            filter_settings.include,
            filter_settings.exclude,
            self.industry_labels[settings.hierarchy],
        )

        return ExposureSettingsMenu._effective_hierarchy(
            self.industries,
            self.industry_labels,
            settings,
            effective_includes,
        )

    def effective_region_hierarchy(
        self,
        filter_settings: RegionSettings,
        settings: HierarchyLevel | HierarchyGroups | None,
    ) -> Mapping[str, Hierarchy]:
        """
        Parameters
        ----------
        filter_settings: RegionSettings
                the settings to use to filter the universe.
        settings: HierarchyLevel | HierarchyGroups | None
                  the settings to use to determine the region factors.

        Returns
        -------
        A dict structure where the keys are the region factor names
        and the values are the region codes that are included in that factor.
        """
        if not settings:
            return {}

        effective_includes = UniverseSettingsMenu.get_effective_includes(
            self.regions[settings.hierarchy],
            filter_settings.include,
            filter_settings.exclude,
            self.region_labels[settings.hierarchy],
        )

        return ExposureSettingsMenu._effective_hierarchy(
            self.regions,
            self.region_labels,
            settings,
            effective_includes,
        )

    def normalize(
        self,
        universe_settings: UniverseSettings,
        exposure_settings: ExposureSettings,
    ) -> ExposureSettings:
        """
        Normalizes the given exposure settings by converting all
        style and substyle codes/labels to their corresponding codes/labels.

        Parameters
        ----------
        universe_settings: UniverseSettings
                the universe settings to use for normalization.
        exposure_settings: ExposureSettings
                the exposure settings to normalize.

        Returns
        -------
        A new exposure settings object with all style and
        substyle code/labels converted to codes/labels.
        """
        if exposure_settings.industries and not (
            exposure_settings.industries.hierarchy
            == universe_settings.industry.hierarchy
        ):
            raise AssertionError(
                "industry schema for universe filter must be identical to schema for "
                f"industry exposures, but is {universe_settings.industry.hierarchy} vs "
                f"{exposure_settings.industries.hierarchy}"
            )

        if exposure_settings.regions and not (
            exposure_settings.regions.hierarchy == universe_settings.region.hierarchy
        ):
            raise AssertionError(
                "region schema for universe filter must be identical to schema for "
                f"region exposures, but is {universe_settings.region.hierarchy} vs "
                f"{exposure_settings.regions.hierarchy}"
            )

        self.validate_settings(exposure_settings)

        effective_industry_includes = UniverseSettingsMenu.get_effective_includes(
            self.industries[universe_settings.industry.hierarchy],
            universe_settings.industry.include,
            universe_settings.industry.exclude,
            self.industry_labels[universe_settings.industry.hierarchy],
        )
        self.validate_hierarchy(
            settings_tools.filter_leaves(
                self.industries, lambda code: code in effective_industry_includes
            ),
            self.industry_labels,
            exposure_settings.industries,
            enforce_full=True,
        )

        effective_region_includes = UniverseSettingsMenu.get_effective_includes(
            self.regions[universe_settings.region.hierarchy],
            universe_settings.region.include,
            universe_settings.region.exclude,
            self.region_labels[universe_settings.region.hierarchy],
        )
        self.validate_hierarchy(
            settings_tools.filter_leaves(
                self.regions, lambda code: code in effective_region_includes
            ),
            self.region_labels,
            exposure_settings.regions,
            enforce_full=True,
        )

        if exposure_settings.styles is None:
            # choose entire style hierarchy by default
            exposure_settings = exposure_settings.model_copy(
                update={"styles": self.styles}
            )

        normalized_styles = self.normalize_styles(exposure_settings.styles)

        if exposure_settings.industries is None:
            normalized_industries = None
        else:
            normalized_industries = (
                HierarchyGroups(
                    hierarchy=exposure_settings.industries.hierarchy,
                    groupings=self.effective_industry_hierarchy(
                        universe_settings.industry,
                        exposure_settings.industries,
                    ),
                )
                if exposure_settings.industries is not None
                else None
            )

        if exposure_settings.regions is None:
            normalized_regions = None
        else:
            normalized_regions = HierarchyGroups(
                hierarchy=exposure_settings.regions.hierarchy,
                groupings=self.effective_region_hierarchy(
                    universe_settings.region,
                    exposure_settings.regions,
                ),
            )

        lookup = {label: code for code, label in self.other_labels.items()}
        normalized_other = {
            k: lookup.get(v, v) for k, v in exposure_settings.other.items()
        }

        return ExposureSettings(
            market=exposure_settings.market,
            styles=normalized_styles,
            industries=normalized_industries,
            regions=normalized_regions,
            other=normalized_other,
        )

    def normalize_styles(
        self, styles: Mapping[str, list[str]] | None
    ) -> dict[str, list[str]]:
        styles = self.styles if styles is None else styles  # styles={} is valid
        lookup = {label: code for code, label in self.style_labels.items()}

        normalized_styles = {}
        for style, substyles in styles.items():  # type: ignore
            normalized_style = lookup.get(style, style)

            normalized_substyles = []
            for substyle in substyles:
                normalized_substyle = lookup.get(substyle, substyle)
                normalized_substyles.append(normalized_substyle)

            normalized_styles[normalized_style] = normalized_substyles
        return normalized_styles

    def all_substyles(
        self,
        settings: ExposureSettings | None = None,
        *,
        labels: bool = False,
    ) -> list[str]:
        """
        Parameters
        ----------
        settings: ExposureSettings, optional
                  the exposure settings to get all substyles for.
        labels: bool, optional
                whether to return the substyles as labels or codes.

        Returns
        -------
        A sorted flat list of all substyles in this settings menu or all
        configured substyles if a settings object is given.
        """
        result: list[str] = []

        if settings is not None and settings.styles is None:
            # choose entire style hierarchy by default
            settings = settings.model_copy(update={"styles": self.styles})

        if settings is not None:
            self.validate_settings(settings)
            for substyles in settings.styles.values():  # type: ignore
                result.extend(substyles)
        else:
            for substyles in self.styles.values():
                result.extend(substyles)

        if labels:
            result = [
                self.style_labels.get(substyle, substyle) for substyle in set(result)
            ]
        else:
            labels_to_codes = {label: code for code, label in self.style_labels.items()}
            result = [
                labels_to_codes.get(substyle, substyle) for substyle in set(result)
            ]
        return sorted(result)

    @staticmethod
    def _effective_hierarchy(
        hierarchies: Mapping[str, Mapping[str, Hierarchy]],
        labels: Mapping[str, Mapping[str, str]],
        settings: HierarchyLevel | HierarchyGroups,
        effective_includes: list[str],
    ) -> Mapping[str, Hierarchy]:
        if isinstance(settings, HierarchyLevel):
            return ExposureSettingsMenu._effective_hierarchy_from_hierarchy_level(
                hierarchies,
                labels,
                settings,
                effective_includes,
            )
        elif isinstance(settings, HierarchyGroups):
            return ExposureSettingsMenu._effective_hierarchy_from_hierarchy_groups(
                hierarchies,
                labels,
                settings,
                effective_includes,
            )
        else:
            raise NotImplementedError(type(settings))

    @staticmethod
    def _effective_hierarchy_from_hierarchy_level(
        hierarchies: Mapping[str, Mapping[str, Hierarchy]],
        labels: Mapping[str, Mapping[str, str]],
        settings: HierarchyLevel,
        effective_includes: list[str],
    ) -> Mapping[str, Hierarchy]:
        if settings.hierarchy is None:
            raise AssertionError(
                """
                Hierarchy must be given, use `normalize` to
                populate the default hierarchy name.
                """,
            )
        hierarchy = hierarchies[settings.hierarchy]
        hierarchy_labels = labels[settings.hierarchy]

        hierarchy_filtered = settings_tools.filter_leaves(
            hierarchy,
            lambda code: code in effective_includes,
        )

        hierarchy_trimmed = settings_tools.trim_to_depth(
            hierarchy_filtered,
            settings.level,
        )

        groups = settings_tools.flatten({"dummy": hierarchy_trimmed}, only_leaves=True)
        result = {}
        for group in groups:
            sub_hierarchy = settings_tools.find_in_hierarchy(hierarchy, group)
            if sub_hierarchy is None or isinstance(sub_hierarchy, int):
                raise AssertionError(f"could not find {group} in {hierarchy}")

            if isinstance(sub_hierarchy, list):
                result[hierarchy_labels[group]] = [group]
            else:
                result[hierarchy_labels[group]] = settings_tools.flatten(
                    sub_hierarchy[group],
                    only_leaves=True,
                )
        return result

    @staticmethod
    def _effective_hierarchy_from_hierarchy_groups(  # noqa: C901
        hierarchies: Mapping[str, Hierarchy],
        labels: Mapping[str, Mapping[str, str]],
        settings: HierarchyGroups,
        effective_includes: list[str] | None = None,
    ) -> Mapping[str, Hierarchy]:
        if settings.hierarchy is None:
            raise AssertionError(
                """
                Hierarchy must be given, use `normalize` to
                populate the default hierarchy name.
                """,
            )

        hierarchy: Mapping[str, Hierarchy] = {
            settings.hierarchy: hierarchies[settings.hierarchy]
        }
        hierarchy_labels = labels[settings.hierarchy]

        hierarchy_filtered = hierarchy
        if effective_includes is not None:
            hierarchy_filtered = settings_tools.filter_leaves(
                hierarchy,
                lambda code: code in effective_includes,
            )

        # leaf codes in the grouping description might be higher level codes
        # or labels, e.g.
        # {
        #   "Energy": ["Energy"],
        #   "Materials": ["15"],
        #   "Exchanges": ["201010", "201020"],
        #   "Asset Managers": ["201010"],
        #   "Banks": ["201020"],
        # }
        #
        # so first we map all leaf codes/labels to the lowest level codes
        # in the actual hierarchy
        groupings = settings.groupings
        actual_leaves = settings_tools.flatten(hierarchy_filtered, only_leaves=True)

        def _expand_leaves_to_actual_leaves(code_or_label: str) -> list[str]:
            if code_or_label in actual_leaves:
                return [code_or_label]
            else:
                v = settings_tools.find_in_hierarchy(hierarchy_filtered, code_or_label)
                if v is None:
                    # must be a label then
                    codes = [
                        k for k, v in hierarchy_labels.items() if v == code_or_label
                    ]
                    if not codes:
                        raise ValueError(
                            "Unknown hierarchy item for hierarchy "
                            f"{settings.hierarchy}: {code_or_label}"
                        )

                    # find the highest level in the hierarchy for possible codes
                    depths = {
                        settings_tools.find_in_hierarchy(
                            hierarchy_filtered,
                            code,
                            return_depth=True,
                        ): code
                        for code in codes
                    }
                    if len(depths) != len(
                        codes,
                    ):
                        raise NotImplementedError(
                            "{codes} - {depths} illegal, all codes my be represented"
                        )
                    v = settings_tools.find_in_hierarchy(
                        hierarchy_filtered,
                        depths[min(depths.keys())],  # type: ignore
                    )
                if isinstance(v, list):
                    return v
                else:
                    if not isinstance(v, Mapping):
                        raise AssertionError(type(v))
                    return settings_tools.flatten(v, only_leaves=True)

        def _map_leaves(
            h: Mapping[str, Hierarchy] | list[str],
        ) -> Mapping[str, Hierarchy] | list[str]:
            if isinstance(h, list):
                return [
                    e
                    for sublist in [_expand_leaves_to_actual_leaves(e) for e in h]
                    for e in sublist
                ]
            else:
                return {k: _map_leaves(v) for k, v in h.items()}

        effective_groupings = _map_leaves(groupings)
        mapped_grouping_leaves = settings_tools.flatten(
            effective_groupings, only_leaves=True
        )
        settings_tools.check_all_leafcodes_exist(
            {settings.hierarchy: effective_groupings}, set(actual_leaves)
        )
        settings_tools.check_unique_hierarchy(
            {settings.hierarchy: {"__DUMMY__": mapped_grouping_leaves}}
        )

        if not isinstance(effective_groupings, Mapping):
            raise AssertionError(type(effective_groupings))
        return effective_groupings

    def describe(self, settings: ExposureSettings | None = None) -> str:
        if settings is not None:
            self.validate_settings(settings)
            hierarchy = settings.styles or self.styles
            standardize_styles = (
                f"\nStandardize Styles: {settings.standardize_styles}\n"
            )
            other = [
                self.other_labels.get(other, other) for other in settings.other.values()
            ]
        else:
            hierarchy = self.styles
            standardize_styles = ""
            other = list(self.other_labels.values())

        style_hierarchy = {}
        for style, substyles in hierarchy.items():
            style_label = self.style_labels.get(style, style)
            style_hierarchy[style_label] = [
                self.style_labels.get(substyle, substyle) for substyle in substyles
            ]

        description = [
            "Style Hierarchy:",
            json.dumps(style_hierarchy, indent=2),
            standardize_styles,
            "Other Exposures:",
            f"{os.linesep.join([f'  - {o}' for o in sorted(other)])}",
        ]

        return os.linesep.join(description)

    @field_validator("industries", "regions", "styles")
    @classmethod
    def check_unique_hierarchy(
        cls: type["ExposureSettingsMenu"],
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        return settings_tools.check_unique_hierarchy(v)

    @field_validator("industries", "regions")
    @classmethod
    def check_nonempty_hierarchy(
        cls: type["ExposureSettingsMenu"],
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        return settings_tools.check_nonempty_hierarchy(v)

    @field_validator("styles")
    @classmethod
    def check_nonempty_hierarchy_if_provided(
        cls: type["ExposureSettingsMenu"],
        v: Mapping[str, Mapping[str, Hierarchy]],
    ) -> Mapping[str, Mapping[str, Hierarchy]]:
        if len(v) == 0:
            return v
        return settings_tools.check_nonempty_hierarchy(v)

    @model_validator(mode="after")
    def check_all_codes_have_labels(self) -> "ExposureSettingsMenu":
        market_errors = settings_tools.check_all_codes_have_labels(
            {"market": [self.market]},
            {"market": self.market_labels},
        )
        industry_errors = settings_tools.check_all_codes_have_labels(
            self.industries,
            self.industry_labels,
        )
        region_errors = settings_tools.check_all_codes_have_labels(
            self.regions,
            self.region_labels,
        )
        style_errors = settings_tools.check_all_codes_have_labels(
            {"styles": self.styles},
            {"styles": self.style_labels},
        )
        other_errors = settings_tools.check_all_codes_have_labels(
            {"other": list(self.other)},
            {"other": self.other_labels},
        )

        errors = (
            market_errors
            + industry_errors
            + region_errors
            + style_errors
            + other_errors
        )
        if errors:
            raise ValueError(os.linesep.join(errors))
        else:
            return self

    def validate_settings(self, settings: ExposureSettings) -> None:
        """
        Validates the given exposure settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: ExposureSettings
                  the exposure settings to validate against.
        """
        self.validate_styles(settings.styles)
        self.validate_hierarchy(
            self.industries,
            self.industry_labels,
            settings.industries,
            enforce_full=False,
        )
        self.validate_hierarchy(
            self.regions, self.region_labels, settings.regions, enforce_full=False
        )
        self.validate_other(settings.other)

    def validate_styles(self, settings: Mapping[str, list[str]] | None) -> None:
        """
        Validates the given style settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: Mapping[str, list[str]]
                  the style settings to validate against.
        """
        if settings is None:
            # nothing to do, default styles will be used
            return

        available_settings = self.styles
        available_labels = self.style_labels.values()

        error_messages = []
        for style, substyles in settings.items():
            if style not in available_settings and style not in available_labels:
                error_messages.append(f"Style {style} does not exist.")
                continue

            if style in available_labels:
                style_code = next(
                    style_code
                    for style_code, style_label in self.style_labels.items()
                    if style_label == style
                )
            else:
                style_code = style

            available_substyles = available_settings[style_code]

            for substyle in substyles:
                if (
                    substyle not in available_substyles
                    and substyle not in available_labels
                ):
                    error_messages.append(f"Substyle {substyle} does not exist.")

            if len(substyles) > len(set(substyles)):
                dupes = {
                    substyle for substyle in substyles if substyles.count(substyle) > 1
                }
                error_messages.append(
                    f"Substyles {', '.join(dupes)} are duplicated for style {style}.",
                )

        if error_messages:
            raise ValueError(os.linesep.join(error_messages))

    @staticmethod
    def validate_hierarchy(
        hierarchies: Mapping[str, Hierarchy],
        labels: Mapping[str, Mapping[str, str]],
        settings: HierarchyLevel | HierarchyGroups | None,
        enforce_full: bool,
    ) -> None:
        if settings is None:
            return

        settings_tools.validate_hierarchy_schema(hierarchies.keys(), settings.hierarchy)

        if isinstance(settings, HierarchyLevel):
            depth = settings_tools.get_depth(hierarchies[settings.hierarchy])
            if depth < settings.level:
                raise ValueError(
                    f"Illegal level {settings.level}, maximum level is {depth}"
                )
        elif isinstance(settings, HierarchyGroups):
            effective_hierarchy = (
                ExposureSettingsMenu._effective_hierarchy_from_hierarchy_groups(
                    hierarchies,
                    labels,
                    settings,
                )
            )

            existing = set(
                settings_tools.flatten(
                    hierarchies[settings.hierarchy], only_leaves=True
                )
            )

            settings_tools.check_all_leafcodes_exist(effective_hierarchy, existing)

            # the hierarchy is a grouping where the leaves map to the actual industry
            # or region hierarchy and anything above are labels for the grouping
            # hence to check for uniqueness we check anything above the leaves
            # and the leaves themselves
            check_hierarchy = {settings.hierarchy: effective_hierarchy}
            check_hierarchy_no_leaves = settings_tools.prune_leaves(check_hierarchy)
            check_hierarchy_only_leaves = settings_tools.flatten(
                check_hierarchy, only_leaves=True
            )
            settings_tools.check_unique_hierarchy(
                {"__DUMMY__": check_hierarchy_no_leaves}
            )

            dupes = [
                item
                for item, count in Counter(check_hierarchy_only_leaves).items()
                if count > 1
            ]
            if dupes:
                raise ValueError(f"Duplicate hierarchy codes: {', '.join(dupes)}")

            # check all codes are used
            if enforce_full:
                configured_codes = set(
                    settings_tools.flatten(effective_hierarchy, only_leaves=True)
                )
                missing = existing - configured_codes
                if missing:
                    raise ValueError(
                        f"Missing hierarchy codes for {settings.hierarchy}: {','.join(missing)}"
                    )
        else:
            raise ValueError(f"unknown settings type {type(settings)}")

    def validate_other(self, settings: Mapping[str, str]) -> None:
        """
        Validates the given other settings against the available settings.

        Will raise an `ValueError` if settings are invalid.

        Parameters
        ----------
        settings: Mapping[str, str]
            the other settings to validate against.
        """
        available_settings = self.other
        available_labels = self.other_labels.values()

        error_messages = []
        for setting in settings.values():
            if setting not in available_settings and setting not in available_labels:
                error_messages.append(f"Other {setting} does not exist.")

        if error_messages:
            raise ValueError(os.linesep.join(error_messages))

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
            self.industries[hierarchy], self.industry_labels[hierarchy]
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
            self.regions[hierarchy], self.region_labels[hierarchy]
        )
