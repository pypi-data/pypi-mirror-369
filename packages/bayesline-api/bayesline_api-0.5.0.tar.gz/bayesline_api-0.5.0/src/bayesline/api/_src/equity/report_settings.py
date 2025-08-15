import os
from abc import ABC
from typing import Annotated, ClassVar, Literal, Type, TypeAlias, Union

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from pydantic.fields import FieldInfo
from typing_extensions import Unpack

from bayesline.api._src.equity.riskmodels_settings import FactorRiskModelSettings
from bayesline.api._src.registry import Settings, SettingsMenu, SettingsTypeMetaData


class ReportAccessorSettings(Settings):

    axes: dict[str, list[str]]
    metric_cols: list[str]
    pivot_cols: list[str]

    # can be used for multi accessors, one entry for each underlying report
    # e.g. extra_cols = name, risk_model, date # noqa: E800
    # e.g. extra_paths = [["My Setting", "US-All", "2024-12-12"]] # noqa: E800
    extra_paths: list[list[str]] = Field(default_factory=list)
    extra_cols: list[str] = Field(default_factory=list)

    linked_reports: list[int] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class MeasureSettings(BaseModel, ABC, frozen=True, extra="forbid"):
    """Defines settings for a measure."""

    type: str

    @property
    def columns(self) -> list[str]:
        return [self.type]

    def __init_subclass__(cls, **kwargs: Unpack[ConfigDict]) -> None:
        super().__init_subclass__(**kwargs)
        # check that every field has a default value, so we can instantiate settings
        # without any argument. Fields defined as a: int = 1, a: int = Field(1), and
        # a: list[int] = Field(default_factory=list) are all valid.
        for f in cls.__annotations__:
            msg = f"{f} not does not have a default value"
            if f not in cls.__dict__:
                raise AssertionError(msg)  # fields without ... = Field(...)
            if isinstance(cls.__dict__[f], FieldInfo):
                if cls.__dict__[f].is_required():
                    raise AssertionError(msg)  # with = Field(...)


class PassThroughFactor2DMeasureSettings(MeasureSettings):
    type: Literal["PassThroughFactor2D"] = Field("PassThroughFactor2D", repr=False)
    name: str = Field("PassThroughFactor2D", description="The name of the measure.")

    @property
    def columns(self) -> list[str]:
        return [self.name]


class HoldingsMeasureSettings(MeasureSettings):
    type: Literal["Holdings"] = Field("Holdings", repr=False)

    @property
    def columns(self) -> list[str]:
        return ["Portfolio", "Benchmark", "Active"]


class ExposureMeasureSettings(MeasureSettings):
    type: Literal["Exposure"] = Field("Exposure", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")

    @property
    def columns(self) -> list[str]:
        return ["Portfolio", "Benchmark", "Active"]


class XSigmaRhoMeasureSettings(MeasureSettings):
    type: Literal["XSigmaRho"] = Field("XSigmaRho", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")
    analytics_space: Literal["absolute", "active", "benchmark"] = Field(
        "absolute",
        description=(
            "Compute the analytics in `absolute` space, `active` space, or compute the "
            "analytics only on the `benchmark`."
        ),
    )

    @property
    def columns(self) -> list[str]:
        return [
            "Exposure (X)",  # X
            "Volatility (\u03c3)",  # σ
            "Correlation (\u03c1)",  # ρ
            "Contribution (X\u03c3\u03c1)",  # Xσρ
        ]


class TimeSeriesXSigmaRhoMeasureSettings(MeasureSettings):
    type: Literal["TimeSeriesXSigmaRho"] = Field("TimeSeriesXSigmaRho", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")
    analytics_space: Literal["absolute", "active", "benchmark"] = Field(
        "absolute",
        description=(
            "Compute the anlytics in `absolute` space, `active` space, or compute the "
            "analytics only on the `benchmark`."
        ),
    )
    backfill_holdings: bool = Field(
        False,
        description="Backfill the latest holdings, accounting for listing/delisting.",
    )

    @property
    def columns(self) -> list[str]:
        return [
            "Exposure (X)",  # X
            "Volatility (\u03c3)",  # σ
            "Correlation (\u03c1)",  # ρ
            "Contribution (X\u03c3\u03c1)",  # Xσρ
        ]


class TimeSeriesBetaMeasureSettings(MeasureSettings):
    type: Literal["TimeSeriesBeta"] = Field("TimeSeriesBeta", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )

    @property
    def columns(self) -> list[str]:
        return [
            "Beta (\u03b2)",  # β
        ]


class HVaRMeasureSettings(MeasureSettings):
    type: Literal["Historical VaR"] = Field("Historical VaR", repr=False)
    alpha: list[float] = Field([0.1, 0.05])

    @property
    def columns(self) -> list[str]:
        return [f"HistVaR {a:.0%}" for a in self.alpha]


class AVaRMeasureSettings(MeasureSettings):
    type: Literal["Analytical VaR"] = Field("Analytical VaR", repr=False)
    alpha: list[float] = Field([0.1, 0.05])

    @property
    def columns(self) -> list[str]:
        return [f"AnVaR {a:.0%}" for a in self.alpha]


class TimeSeriesVolatilityMeasureSettings(MeasureSettings):
    type: Literal["TimeSeriesVolatility"] = Field("TimeSeriesVolatility", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    ddof: int = Field(1, description="The degrees of freedom to use for the volality")


class CumsumMeasureSettings(MeasureSettings):
    type: Literal["Cumsum"] = Field("Cumsum", repr=False)


class DrawdownMeasureSettings(MeasureSettings):
    type: Literal["Drawdown"] = Field("Drawdown", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")


class MovingAverageMeasureSettings(MeasureSettings):
    type: Literal["MovingAverage"] = Field("MovingAverage", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    var: Literal["r2", "sigma2", "sigma"] = Field(
        "r2", description="The variable to average"
    )

    @property
    def columns(self) -> list[str]:
        return [f"{self.type} {self.var}"]


class FactorMovingAverageMeasureSettings(MeasureSettings):
    type: Literal["FactorMovingAverage"] = Field("FactorMovingAverage", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    var: Literal["abs_t", "p", "p1", "p5"] = Field(
        "p", description="The variable to average"
    )

    @property
    def columns(self) -> list[str]:
        return [f"{self.type} {self.var}"]


class MovingAverageRSquaredMeasureSettings(MeasureSettings):
    type: Literal["MovingAverageRSquared"] = Field("MovingAverageRSquared", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")
    window: str = Field("6mo", description="The size of the rolling window")


class VolForecastMeasureSettings(MeasureSettings):
    type: Literal["VolForecast"] = Field("VolForecast", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    metric: Literal["qlike", "mse", "mae", "bias"] = Field(
        "qlike", description="The metric to use"
    )
    ddof: int = Field(1, description="The degrees of freedom to use for the stability")

    @property
    def columns(self) -> list[str]:
        return [
            "VolForecast",
            "VolForecastRealized",
            "VolForecastStability",
            "VolForecastLoss",
        ]


class FactorVolForecastMeasureSettings(MeasureSettings):
    type: Literal["FactorVolForecast"] = Field("FactorVolForecast", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    metric: Literal["qlike", "mse", "mae", "bias"] = Field(
        "qlike", description="The metric to use"
    )
    ddof: int = Field(1, description="The degrees of freedom to use for the stability")

    @property
    def columns(self) -> list[str]:
        return [
            "VolForecast",
            "VolForecastRealized",
            "VolForecastStability",
            "VolForecastLoss",
        ]


class FactorCovarianceMeasureSettings(MeasureSettings):
    type: Literal["FactorCovariance"] = Field("FactorCovariance", repr=False)


class IdiosyncraticReturnMeasureSettings(MeasureSettings):
    type: Literal["IdiosyncraticReturn"] = Field("IdiosyncraticReturn", repr=False)


class IdiosyncraticVolatilityMeasureSettings(MeasureSettings):
    type: Literal["IdiosyncraticVolatility"] = Field(
        "IdiosyncraticVolatility", repr=False
    )


class FactorIdioMeasureSettings(MeasureSettings):
    type: Literal["FactorIdio"] = Field("FactorIdio", repr=False)


class ForecastBacktestMeasureSettings(MeasureSettings):
    type: Literal["ForecastBacktest"] = Field("ForecastBacktest", repr=False)
    window: str = Field("6mo", description="The size of the rolling window")
    ddof: int = Field(1, description="The degrees of freedom to use for the stability")

    @property
    def columns(self) -> list[str]:
        return ["GlobalMinVolPortVolatility", "GlobalMinVolPortPredictedVolatility"]


class BrinsonAttributionMeasureSettings(MeasureSettings):
    type: Literal["BrinsonAttribution"] = Field("BrinsonAttribution", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")
    multiperiod_aggregation: Literal["none", "optimized"] = Field("none")
    return_aggregation_type: Literal["arithmetic", "geometric"] = Field("geometric")

    @property
    def columns(self) -> list[str]:
        return ["Allocation", "Selection", "Interaction", "Active"]


class FactorAttributionMeasureSettings(MeasureSettings):
    type: Literal["FactorAttribution"] = Field("FactorAttribution", repr=False)
    rescale_bench: bool = Field(
        True,
        description="Rescale the benchmark holdings to sum to the sum of the holdings.",
    )
    normalize_holdings: bool = Field(True, description="Make holdings sum to one.")
    multiperiod_aggregation: Literal["none", "optimized"] = Field("none")
    return_aggregation_type: Literal["arithmetic", "geometric"] = Field("geometric")

    @property
    def columns(self) -> list[str]:
        return ["Portfolio", "Benchmark", "Active"]


class PortfolioStressTestMeasureSettings(MeasureSettings):
    type: Literal["PortfolioStressTest"] = Field("PortfolioStressTest", repr=False)
    shock_size: float = Field(0.1, description="The size of the shock to apply.")

    @property
    def columns(self) -> list[str]:
        return ["Impact"]


class AssetStressTestMeasureSettings(MeasureSettings):
    type: Literal["AssetStressTest"] = Field("AssetStressTest", repr=False)
    shock_size: float = Field(
        1.0, description="The size of the shock to apply in standard deviations."
    )

    @property
    def columns(self) -> list[str]:
        return ["Impact"]


class AssetHoldingsMeasureSettings(MeasureSettings):
    type: Literal["AssetHoldings"] = Field("AssetHoldings", repr=False)

    @property
    def columns(self) -> list[str]:
        return [
            *["Position", "Position Bench", "Position Diff"],
            *["Holdings", "Holdings Bench", "Holdings Diff"],
            *["Weight", "Weight Bench", "Weight Diff"],
            *["Rank", "Rank Bench", "Rank Diff"],
        ]


MeasureSettingsType: TypeAlias = Union[tuple(MeasureSettings.__subclasses__())]  # type: ignore
MeasureSettingsClassType = Type[MeasureSettingsType]

ALL_HOLDINGS_MEASURE_TYPES = [
    HoldingsMeasureSettings,
]
ALL_EXPOSURE_MEASURE_TYPES = [
    ExposureMeasureSettings,
]
ALL_XSR_MEASURE_TYPES = [
    XSigmaRhoMeasureSettings,
]
ALL_TSXSR_MEASURE_TYPES = [
    TimeSeriesXSigmaRhoMeasureSettings,
]
ALL_TS_BETA_MEASURE_TYPES = [
    TimeSeriesBetaMeasureSettings,
]
ALL_VAR_MEASURE_TYPES = [
    HVaRMeasureSettings,
    AVaRMeasureSettings,
]
ALL_FACTOR_TS_MEASURE_TYPES = [
    TimeSeriesVolatilityMeasureSettings,
    CumsumMeasureSettings,
    DrawdownMeasureSettings,
]
ALL_RISK_MODEL_FIT_MEASURE_TYPES = [
    MovingAverageMeasureSettings,
]
ALL_RISK_MODEL_FIT_FACTOR_MEASURE_TYPES = [
    FactorMovingAverageMeasureSettings,
]
ALL_RISK_MODEL_PORTFOLIO_FIT_MEASURE_TYPES = [
    MovingAverageRSquaredMeasureSettings,
]
ALL_FACTOR_FORECAST_LOSS_MEASURE_TYPES = [
    FactorVolForecastMeasureSettings,
]
ALL_FORECAST_LOSS_MEASURE_TYPES = [
    VolForecastMeasureSettings,
]
ALL_FACTOR_COVARIANCE_MEASURE_TYPES = [
    FactorCovarianceMeasureSettings,
]
ALL_IDIOSYNCRATIC_VOLATILITY_MEASURE_TYPES = [
    IdiosyncraticVolatilityMeasureSettings,
]
ALL_IDIOSYNCRATIC_RETURN_MEASURE_TYPES = [
    IdiosyncraticReturnMeasureSettings,
]
ALL_FACTOR_IDIO_MEASURE_TYPES = [
    FactorIdioMeasureSettings,
]
ALL_STYLE_CORRELATION_MEASURE_TYPES = [
    PassThroughFactor2DMeasureSettings,
]
ALL_STYLE_INDUSTRY_EXPOSURE_MEASURE_TYPES = [
    PassThroughFactor2DMeasureSettings,
]
ALL_FORECAST_BACKTEST_MEASURE_TYPES = [
    ForecastBacktestMeasureSettings,
]
ALL_BRINSON_ATTRIBUTION_MEASURE_TYPES = [
    BrinsonAttributionMeasureSettings,
]
ALL_FACTOR_ATTRIBUTION_MEASURE_TYPES = [
    FactorAttributionMeasureSettings,
]
ALL_PORTFOLIO_STRESS_TEST_MEASURE_TYPES = [
    PortfolioStressTestMeasureSettings,
]
ALL_ASSET_STRESS_TEST_MEASURE_TYPES = [
    AssetStressTestMeasureSettings,
]
ALL_ASSET_HOLDINGS_MEASURE_TYPES = [
    AssetHoldingsMeasureSettings,
]


def _get_default_measures(
    measure_types: list[MeasureSettingsClassType],
) -> list[MeasureSettingsType]:
    return [m() for m in measure_types]


class ConcreteReportSettings(BaseModel, ABC, frozen=True, extra="forbid"):
    type: str
    lagged_holdings: ClassVar[bool] = False
    measures: list[MeasureSettingsType] = Field(
        description="The measures to include in the report.",
    )


class HoldingsReportSettings(ConcreteReportSettings):
    """Defines settings to build a holdings report."""

    type: Literal["Holdings report"] = Field("Holdings report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_HOLDINGS_MEASURE_TYPES),
        description="The measures to include in the report.",
    )


class ExposureReportSettings(ConcreteReportSettings):
    """Defines settings to build an exposure report."""

    type: Literal["Exposure report"] = Field("Exposure report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_EXPOSURE_MEASURE_TYPES),
        description="The measures to include in the report.",
    )


class XSRReportSettings(ConcreteReportSettings):
    """Defines settings to build an XSR report."""

    type: Literal["XSR report"] = Field("XSR report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_XSR_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class TSXSRReportSettings(ConcreteReportSettings):
    """Defines settings to build a time-series XSR report."""

    type: Literal["TSXSR report"] = Field("TSXSR report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_TSXSR_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class TSBetaReportSettings(ConcreteReportSettings):
    """Defines settings to build a time-series Beta report."""

    type: Literal["TS Beta report"] = Field("TS Beta report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_TS_BETA_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class VaRReportSettings(ConcreteReportSettings):
    """Defines settings to build a VaR report."""

    type: Literal["VaR report"] = Field("VaR report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_VAR_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    lookback: int = Field(1000, description="The lookback period for the estimation.")


class FactorTSReportSettings(ConcreteReportSettings):
    """Defines settings to build a factor time-series report."""

    type: Literal["Factor TS report"] = Field("Factor TS report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_FACTOR_TS_MEASURE_TYPES),  # type: ignore
        description="The measures to include in the report.",
    )


class RiskModelFitReportSettings(ConcreteReportSettings):
    """Defines settings to build a risk model fit report."""

    type: Literal["Risk Model Fit report"] = Field("Risk Model Fit report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_RISK_MODEL_FIT_MEASURE_TYPES),
        description="The measures to include in the report.",
    )


class RiskModelFitFactorReportSettings(ConcreteReportSettings):
    """Defines settings to build a risk model fit report at the factor level."""

    type: Literal["Risk Model Fit Factor report"] = Field(
        "Risk Model Fit Factor report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_RISK_MODEL_FIT_FACTOR_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class RiskModelPortfolioFitReportSettings(ConcreteReportSettings):
    """Defines settings to build a risk model fit report at the portfolio level."""

    type: Literal["Risk Model Portfolio Fit report"] = Field(
        "Risk Model Portfolio Fit report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_RISK_MODEL_PORTFOLIO_FIT_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class FactorForecastLossReportSettings(ConcreteReportSettings):
    """Defines settings to build a forecast loss report."""

    type: Literal["Factor Forecast Loss report"] = Field(
        "Factor Forecast Loss report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_FACTOR_FORECAST_LOSS_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    horizons: list[int] = Field([1, 5, 21], description="The forecast horizons to use.")
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )


class AssetForecastLossReportSettings(ConcreteReportSettings):
    """Defines settings to build a forecast loss report."""

    type: Literal["Forecast Loss report"] = Field("Forecast Loss report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_FORECAST_LOSS_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    horizons: list[int] = Field([1, 5, 21], description="The forecast horizons to use.")
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class FactorCovarianceReportSettings(ConcreteReportSettings):
    """Defines settings to build a factor covariance report."""

    type: Literal["Factor Covariance report"] = Field(
        "Factor Covariance report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_FACTOR_COVARIANCE_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )


class IdiosyncraticReturnReportSettings(ConcreteReportSettings):
    """Defines settings to build an idiosyncratic return report."""

    type: Literal["Idiosyncratic Return report"] = Field(
        "Idiosyncratic Return report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_IDIOSYNCRATIC_RETURN_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class IdiosyncraticVolatilityReportSettings(ConcreteReportSettings):
    """Defines settings to build an idiosyncratic volatility report."""

    type: Literal["Idiosyncratic Volatility report"] = Field(
        "Idiosyncratic Volatility report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_IDIOSYNCRATIC_VOLATILITY_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class FactorIdioReportSettings(ConcreteReportSettings):
    """Defines settings to build a factor vcov and idio report."""

    type: Literal["Factor Idio report"] = Field("Factor Idio report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_FACTOR_IDIO_MEASURE_TYPES),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class StyleCorrelationReportSettings(ConcreteReportSettings):
    """Defines settings to build a style correlation report."""

    type: Literal["Style Correlation report"] = Field(
        "Style Correlation report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_STYLE_CORRELATION_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class StyleIndustryExposureReportSettings(ConcreteReportSettings):
    """Defines settings to build a style industry exposure report."""

    type: Literal["Style Industry Exposure report"] = Field(
        "Style Industry Exposure report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_STYLE_INDUSTRY_EXPOSURE_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class ForecastBacktestReportSettings(ConcreteReportSettings):
    """Defines settings to build a forecast backtest report."""

    type: Literal["Forecast Backtest report"] = Field(
        "Forecast Backtest report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_FORECAST_BACKTEST_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    horizons: list[int] = Field([1, 5, 21], description="The forecast horizons to use.")
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class BrinsonAttributionReportSettings(ConcreteReportSettings):
    """Defines settings to build a Brinson attribution report."""

    type: Literal["Brinson Attribution report"] = Field(
        "Brinson Attribution report", repr=False
    )
    lagged_holdings: ClassVar[bool] = True
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_BRINSON_ATTRIBUTION_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class FactorAttributionReportSettings(ConcreteReportSettings):
    """Defines settings to build a factor attribution report."""

    type: Literal["Factor Attribution report"] = Field(
        "Factor Attribution report", repr=False
    )
    lagged_holdings: ClassVar[bool] = True
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_FACTOR_ATTRIBUTION_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )


class PortfolioStressTestReportSettings(ConcreteReportSettings):
    """Defines settings to build a portfolio stress test report."""

    type: Literal["Portfolio Stress Test report"] = Field(
        "Portfolio Stress Test report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_PORTFOLIO_STRESS_TEST_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class AssetStressTestReportSettings(ConcreteReportSettings):
    """Defines settings to build an asset stress test report."""

    type: Literal["Asset Stress Test report"] = Field(
        "Asset Stress Test report", repr=False
    )
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(
            ALL_ASSET_STRESS_TEST_MEASURE_TYPES
        ),
        description="The measures to include in the report.",
    )
    halflife_factor_vol: int = Field(
        42, description="The half-life for the factor volatility."
    )
    halflife_factor_adj: int | None = Field(
        None,
        description=(
            "The half-life for the factor adjustment. "
            "If None, no adjustment is applied."
        ),
    )
    halflife_factor_cor: int = Field(
        126, description="The half-life for the factor correlation."
    )
    halflife_idio_vol: int = Field(
        42, description="The half-life for the idiosyncratic volatility."
    )
    shrink_factor_cor_method: Literal["LIS", "QIS", "GIS"] | None = Field(
        None,
        description=(
            "The method to use for the shrinkage of the factor correlation. If None, "
            "don't shrink."
        ),
    )
    shrink_factor_cor_length: int | None = Field(
        1008,
        description=(
            "If a shrinkage method is provided, the length of the shrinkage for the "
            "factor correlation."
        ),
    )
    shrink_factor_cor_standardized: bool = Field(
        False,
        description=(
            "If True, the correlation matrix is combined with an estimate based on the "
            "standardized returns. The halflife_factor_adj is used for the weights."
        ),
    )
    overlap_factor_vol: int = Field(
        0, description="The overlap for the factor volatility."
    )
    overlap_factor_vol_halflife_override: int | None = Field(
        None,
        description="The halflife override for the factor volatility for lagged returns.",
    )
    overlap_factor_cor: int = Field(
        0, description="The overlap for the factor correlation."
    )
    overlap_idio_vol: int = Field(
        0, description="The overlap for the idiosyncratic volatility."
    )
    overlap_idio_vol_halflife_override: int | None = Field(
        None,
        description=(
            "The halflife override for the idiosyncratic volatility for lagged returns."
        ),
    )
    shrink_idio_vol: float = Field(
        0.0, description="The shrinkage factor for the idiosyncratic volatility."
    )


class AssetHoldingsReportSettings(ConcreteReportSettings):
    """Defines settings to build an asset holdings report."""

    type: Literal["Asset Holdings report"] = Field("Asset Holdings report", repr=False)
    measures: list[MeasureSettingsType] = Field(
        default_factory=lambda: _get_default_measures(ALL_ASSET_HOLDINGS_MEASURE_TYPES),
        description="The measures to include in the report.",
    )


ConcreteReportSettingsType: TypeAlias = Union[tuple(ConcreteReportSettings.__subclasses__())]  # type: ignore


class ReportSettings(Settings):
    """
    Defines settings to build a report.
    """

    report: ConcreteReportSettingsType
    risk_model: Annotated[
        str | int | FactorRiskModelSettings,
        Field(
            description="The risk model to use for the report.",
        ),
        SettingsTypeMetaData[str | int | FactorRiskModelSettings](
            references=FactorRiskModelSettings
        ),
    ]


class ConcreteReportSettingsMenu(SettingsMenu, ABC):

    measure_types: ClassVar[list[MeasureSettingsClassType]] = []

    def validate_settings(self, settings: ReportSettings) -> None:
        # TODO implement
        pass

    def describe(self, settings: ReportSettings | None = None) -> str:
        # TODO importment
        return ""


class HoldingsReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_HOLDINGS_MEASURE_TYPES


class ExposureReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_EXPOSURE_MEASURE_TYPES


class XSRReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_XSR_MEASURE_TYPES


class TSXSRReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_TSXSR_MEASURE_TYPES


class TSBetaReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_TS_BETA_MEASURE_TYPES


class VaRReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = ALL_VAR_MEASURE_TYPES


class FactorTSReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FACTOR_TS_MEASURE_TYPES  # type: ignore
    )


class RiskModelFitReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_RISK_MODEL_FIT_MEASURE_TYPES
    )


class RiskModelFitFactorReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_RISK_MODEL_FIT_FACTOR_MEASURE_TYPES
    )


class RiskModelPortfolioFitReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_RISK_MODEL_FIT_MEASURE_TYPES
    )


class FactorForecastLossReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FORECAST_LOSS_MEASURE_TYPES  # type: ignore
    )


class AssetForecastLossReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FORECAST_LOSS_MEASURE_TYPES  # type: ignore
    )


class FactorCovarianceReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FACTOR_COVARIANCE_MEASURE_TYPES
    )


class IdiosyncraticReturnReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_IDIOSYNCRATIC_RETURN_MEASURE_TYPES
    )


class IdiosyncraticVolatilityReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_IDIOSYNCRATIC_VOLATILITY_MEASURE_TYPES
    )


class FactorIdioReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FACTOR_IDIO_MEASURE_TYPES
    )


class StyleCorrelationReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_STYLE_CORRELATION_MEASURE_TYPES
    )


class StyleIndustryExposureReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_STYLE_INDUSTRY_EXPOSURE_MEASURE_TYPES
    )


class ForecastBacktestReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FORECAST_BACKTEST_MEASURE_TYPES
    )


class BrinsonAttributionReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_BRINSON_ATTRIBUTION_MEASURE_TYPES
    )


class FactorAttributionReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_FACTOR_ATTRIBUTION_MEASURE_TYPES
    )


class PortfolioStressTestReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_PORTFOLIO_STRESS_TEST_MEASURE_TYPES
    )


class AssetStressTestReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_ASSET_STRESS_TEST_MEASURE_TYPES
    )


class AssetHoldingsReportSettingsMenu(ConcreteReportSettingsMenu):
    measure_types: ClassVar[list[MeasureSettingsClassType]] = (
        ALL_ASSET_HOLDINGS_MEASURE_TYPES
    )


class ReportSettingsMenu(SettingsMenu[ReportSettings]):
    """
    Defines available report settings to build a report.
    """

    hld: ConcreteReportSettingsMenu = HoldingsReportSettingsMenu()
    exp: ConcreteReportSettingsMenu = ExposureReportSettingsMenu()
    xsr: ConcreteReportSettingsMenu = XSRReportSettingsMenu()
    tsx: ConcreteReportSettingsMenu = TSXSRReportSettingsMenu()
    bet: ConcreteReportSettingsMenu = TSBetaReportSettingsMenu()
    var: ConcreteReportSettingsMenu = VaRReportSettingsMenu()
    fts: ConcreteReportSettingsMenu = FactorTSReportSettingsMenu()
    rmf: ConcreteReportSettingsMenu = RiskModelFitReportSettingsMenu()
    rms: ConcreteReportSettingsMenu = RiskModelFitFactorReportSettingsMenu()
    rmp: ConcreteReportSettingsMenu = RiskModelPortfolioFitReportSettingsMenu()
    ffl: ConcreteReportSettingsMenu = FactorForecastLossReportSettingsMenu()
    afl: ConcreteReportSettingsMenu = AssetForecastLossReportSettingsMenu()
    fcr: ConcreteReportSettingsMenu = FactorCovarianceReportSettingsMenu()
    irr: ConcreteReportSettingsMenu = IdiosyncraticReturnReportSettingsMenu()
    ivr: ConcreteReportSettingsMenu = IdiosyncraticVolatilityReportSettingsMenu()
    fni: ConcreteReportSettingsMenu = FactorIdioReportSettingsMenu()
    scr: ConcreteReportSettingsMenu = StyleCorrelationReportSettingsMenu()
    six: ConcreteReportSettingsMenu = StyleIndustryExposureReportSettingsMenu()
    fbt: ConcreteReportSettingsMenu = ForecastBacktestReportSettingsMenu()
    bat: ConcreteReportSettingsMenu = BrinsonAttributionReportSettingsMenu()
    fat: ConcreteReportSettingsMenu = FactorAttributionReportSettingsMenu()
    pst: ConcreteReportSettingsMenu = PortfolioStressTestReportSettingsMenu()
    ast: ConcreteReportSettingsMenu = AssetStressTestReportSettingsMenu()
    ahd: ConcreteReportSettingsMenu = AssetHoldingsReportSettingsMenu()

    def describe(self, settings: ReportSettings | None = None) -> str:
        # TODO
        if settings is not None:
            return os.linesep.join([f"Risk Model: {settings.risk_model}"])
        else:
            return "NA"

    def validate_settings(self, settings: ReportSettings) -> None:
        # TODO
        pass
