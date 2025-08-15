import datetime as dt
from typing import Annotated, Literal, cast

from pydantic import BaseModel, Field, field_validator

from bayesline.api._src.equity.calendar_settings import (
    CalendarSettings,
    CalendarSettingsMenu,
)
from bayesline.api._src.equity.exposure_settings import ExposureSettingsMenu
from bayesline.api._src.equity.modelconstruction_settings import (
    ModelConstructionSettingsMenu,
)
from bayesline.api._src.equity.universe_settings import UniverseSettingsMenu
from bayesline.api._src.registry import Settings, SettingsMenu


class RiskDatasetUpdateResult(BaseModel): ...


class RiskDatasetReferencedExposureSettings(BaseModel, frozen=True, extra="forbid"):

    exposure_type: Literal["referenced"] = "referenced"

    market_factor_groups: list[str] | None = Field(
        None,
        description=(
            "The factor groups for market cap factors. If None, the market factor from "
            "the reference dataset is used."
        ),
    )
    region_factor_groups: list[str] | None = Field(
        None,
        description=(
            "The factor groups for region factors. If None, the region factor from "
            "the reference dataset is used."
        ),
    )
    industry_factor_groups: list[str] | None = Field(
        None,
        description=(
            "The factor groups for industry factors. If None, the industry factor from "
            "the reference dataset is used."
        ),
    )
    style_factor_groups: list[str] | None = Field(
        None,
        description=(
            "The factor groups for style factors. If None, the style factor from "
            "the reference dataset is used."
        ),
    )
    other_factor_groups: list[str] | None = Field(
        None,
        description=(
            "The factor groups for other factors. If None, the other factor from "
            "the reference dataset is used."
        ),
    )

    @field_validator(
        "market_factor_groups",
        "region_factor_groups",
        "industry_factor_groups",
        "style_factor_groups",
        "other_factor_groups",
        mode="before",
    )
    @classmethod
    def _ensure_list(cls, v: str | list[str] | None) -> list[str] | None:
        if isinstance(v, str):
            return [v]
        return v


class RiskDatasetUploadedExposureSettings(BaseModel, frozen=True, extra="forbid"):

    exposure_type: Literal["uploaded"] = "uploaded"

    exposure_source: str = Field(description="The uploaded source of the exposures.")

    market_factor_group: str | None = Field(
        None, description="The factor group for market cap factors."
    )
    region_factor_group: str | None = Field(
        None, description="The factor group for region factors."
    )
    industry_factor_group: str | None = Field(
        None, description="The factor group for industry factors."
    )
    style_factor_group: str | None = Field(
        None, description="The factor group for style factors."
    )
    other_factor_group: str | None = Field(
        None, description="The factor group for other factors."
    )

    style_factor_fill_miss: bool = Field(
        True,
        description="Whether to fill missing values for the style factors.",
    )
    style_factor_huberize: bool = Field(
        True,
        description="Whether to huberize the style factors.",
    )


class RiskDatasetHuberRegressionExposureSettings(
    BaseModel, frozen=True, extra="forbid"
):

    exposure_type: Literal["huber_regression"] = "huber_regression"

    tsfactors_source: str = Field(description="The source of the timeseries factors.")
    factor_group: str = Field(
        "huber_style", description="The factor group name to use for the regression."
    )
    include: list[str] | Literal["All"] = Field(
        "All", description="The factors to include in the regression."
    )
    exclude: list[str] = Field(
        default_factory=list,
        description="The factors to exclude from the regression.",
    )
    fill_miss: bool = Field(True)
    window: int = Field(126, description="The window for the rolling regressions.")
    epsilon: float = Field(1.35, description="The epsilon for the huber regression.")
    alpha: float = Field(0.0001, description="The alpha for the huber regression.")
    alpha_start: float = Field(10.0, description="The alpha when no data is available.")
    student_t_level: float | None = Field(
        None,
        description=(
            "The level for the student t-test. If a test for the significance of the "
            "factor exposure is not rejected, the factor exposure is set to zero. If "
            "None, no test is run and the factor exposure is not set to zero."
        ),
        ge=0.0,
        le=1.0,
    )
    clip: tuple[float | None, float | None] = Field(
        (None, None),
        description=(
            "The clipping lower and upper bounds for the resulting exposures, before "
            "potential huberization."
        ),
    )
    huberize: bool = Field(
        True,
        description="Whether to huberize the resulting exposures.",
    )
    huberize_maintain_zeros: bool = Field(
        False,
        description="Whether to maintain zeros when huberizing the exposures.",
    )
    impute: bool = Field(
        True,
        description="Whether to impute missing values for the resulting exposures.",
    )
    currency: str = Field("USD", description="The currency to convert all returns to.")
    calendar: CalendarSettings = Field(
        default_factory=CalendarSettings.default,
        description="The calendar to use for the rolling regressions.",
    )


class RiskDatasetUnitExposureSettings(BaseModel, frozen=True, extra="forbid"):

    exposure_type: Literal["unit"] = "unit"

    factor: str = Field(description="The factor to use for the unit exposures.")
    factor_group: str = Field(
        description="The factor group to use for the unit exposures."
    )
    factor_type: Literal["market", "region", "industry"] = Field(
        "market", description="The type of factor to use for the unit exposures."
    )

    @classmethod
    def region(
        cls: type["RiskDatasetUnitExposureSettings"],
    ) -> "RiskDatasetUnitExposureSettings":
        return cls(
            factor="world",
            factor_group="region",
            factor_type="region",
        )

    @classmethod
    def industry(
        cls: type["RiskDatasetUnitExposureSettings"],
    ) -> "RiskDatasetUnitExposureSettings":
        return cls(
            factor="industry",
            factor_group="industry",
            factor_type="industry",
        )

    @classmethod
    def market(
        cls: type["RiskDatasetUnitExposureSettings"],
    ) -> "RiskDatasetUnitExposureSettings":
        return cls(
            factor="market",
            factor_group="market",
            factor_type="market",
        )


RiskDatasetExposureSettings = Annotated[
    RiskDatasetReferencedExposureSettings
    | RiskDatasetUploadedExposureSettings
    | RiskDatasetHuberRegressionExposureSettings
    | RiskDatasetUnitExposureSettings,
    Field(discriminator="exposure_type"),
]


class RiskDatasetSettings(Settings):

    reference_dataset: str | int = Field(
        description=(
            "The dataset (either name or global int identifier) to use as a basis "
            "for the new dataset. All data will be sourced from this dataset."
        ),
        examples=["Bayesline-Global", 1],
    )

    exposures: list[RiskDatasetExposureSettings] = Field(
        default_factory=lambda: [
            cast(RiskDatasetExposureSettings, RiskDatasetReferencedExposureSettings())
        ],
        description=(
            "The exposures to use for the new dataset. By default the reference dataset "
            "is copied as a basis for the new dataset."
        ),
    )
    exchange_codes: list[str] | None = Field(
        default=None,
        description="The exchange codes to filter the reference dataset down to.",
    )
    trim_assets: Literal["none", "asset_union", "ccy_union"] = Field(
        "ccy_union",
        description=(
            "Whether to trim the assets based on the uploaded exposures. "
            "If 'none', the assets are not trimmed. "
            "If 'asset_union', the assets are trimmed to the union of the asset ids in "
            "the uploaded exposures. "
            "If 'ccy_union', the assets are trimmed to the union of all currencies in "
            "the uploaded exposures."
        ),
    )
    trim_start_date: Literal["none", "earliest_start", "latest_start"] | dt.date = (
        Field(
            "earliest_start",
            description=(
                "Whether to trim the start date based on the uploaded exposures. "
                "If 'none', the start date is not trimmed. "
                "If 'earliest_start', the start date is trimmed to the earliest start "
                "date of the uploaded exposures, or the updoaded exposures and the "
                "reference dateset when referenced exposures are provided. "
                "If 'latest_start', the start date is trimmed to the latest start date "
                "the uploaded exposures, or the updoaded exposures and the reference "
                "dateset when referenced exposures are provided. "
                "If a date is provided, the start date is trimmed to the provided date."
            ),
        )
    )
    trim_end_date: Literal["none", "earliest_end", "latest_end"] | dt.date = Field(
        "latest_end",
        description=(
            "Whether to trim the end date based on the uploaded exposures. "
            "If 'none', the end date is not trimmed. "
            "If 'earliest_end', the end date is trimmed to the earliest end "
            "date of the uploaded exposures, or the updoaded exposures and the "
            "reference dateset when referenced exposures are provided. "
            "If 'latest_end', the end date is trimmed to the latest end date of "
            "the uploaded exposures, or the updoaded exposures and the reference "
            "dateset when referenced exposures are provided. "
            "If a date is provided, the end date is trimmed to the provided date."
        ),
    )

    estimation_universe: Literal[
        "from_reference", "from_coverage", "from_uploaded_exposures"
    ] = Field(
        "from_reference",
        description=(
            "The subset of assets to be marked as eligible to include for estimation "
            "purposes (i.e. the estimation universe)."
            "If 'from_reference', the estimation universe markers from the reference "
            "dataset are used. "
            "If 'from_coverage', the entire coverage universe is used."
            "If 'from_uploaded_exposures', every asset/date combination that came in "
            "through an uploaded exposure is marked as eligible for estimation."
        ),
    )


class RiskDatasetSettingsMenu(
    SettingsMenu[RiskDatasetSettings], frozen=True, extra="forbid"
):
    def describe(self, settings: RiskDatasetSettings | None = None) -> str:
        return ""

    def validate_settings(self, settings: RiskDatasetSettings) -> None:
        pass


class RiskDatasetProperties(BaseModel):

    calendar_settings_menu: CalendarSettingsMenu
    universe_settings_menu: UniverseSettingsMenu
    exposure_settings_menu: ExposureSettingsMenu
    modelconstruction_settings_menu: ModelConstructionSettingsMenu
