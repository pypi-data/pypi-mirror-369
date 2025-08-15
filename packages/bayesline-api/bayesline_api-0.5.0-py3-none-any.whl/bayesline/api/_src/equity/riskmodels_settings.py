import os
from itertools import zip_longest
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, PositiveInt

from bayesline.api._src.equity.exposure_settings import ExposureSettings
from bayesline.api._src.equity.modelconstruction_settings import (
    ModelConstructionSettings,
)
from bayesline.api._src.equity.universe_settings import UniverseSettings
from bayesline.api._src.registry import Settings, SettingsMenu, SettingsTypeMetaData


def ensure_list(value: Any) -> Any:
    if isinstance(value, list | tuple):
        return value
    return [value]


class FactorRiskModelSettings(Settings):
    """
    Defines all settings needed to build a factor risk model.
    """

    @classmethod
    def default(cls, *, dataset: str | None = None) -> "FactorRiskModelSettings":
        return cls(
            universe=[UniverseSettings(dataset=dataset)],
            exposures=[ExposureSettings.default()],
            modelconstruction=[ModelConstructionSettings.default()],
        )

    universe: Annotated[
        list[str | int | UniverseSettings],
        BeforeValidator(ensure_list),
        Field(
            description="The universe to build the factor risk model on.",
            default_factory=lambda: [UniverseSettings.default()],
            min_length=1,
            max_length=1,
        ),
        SettingsTypeMetaData[list[str | int | UniverseSettings]](
            references=UniverseSettings,
            extractor=lambda x: [r for r in x if not isinstance(r, UniverseSettings)],
        ),
    ]

    exposures: Annotated[
        list[str | int | ExposureSettings],
        BeforeValidator(ensure_list),
        Field(
            description="The exposures to build the factor risk model on.",
            default_factory=lambda: [ExposureSettings.default()],
            min_length=1,
        ),
        SettingsTypeMetaData[str | int | ExposureSettings](
            references=ExposureSettings,
            extractor=lambda x: [r for r in x if not isinstance(r, ExposureSettings)],
        ),
    ]

    modelconstruction: Annotated[
        list[str | int | ModelConstructionSettings],
        BeforeValidator(ensure_list),
        Field(
            description="The model construction settings to use for the factor risk model.",
            default_factory=lambda: [ModelConstructionSettings.default()],
            min_length=1,
        ),
        SettingsTypeMetaData[str | int | ModelConstructionSettings](
            references=ModelConstructionSettings,
            extractor=lambda x: [
                r for r in x if not isinstance(r, ModelConstructionSettings)
            ],
        ),
    ]
    halflife_idio_adj: PositiveInt | None = Field(
        None,
        description=(
            "The half-life for the idio adjustment. "
            "If None, no adjustment is applied."
        ),
    )


class FactorRiskModelSettingsMenu(SettingsMenu, frozen=True, extra="forbid"):
    """
    Defines available settings to build a factor risk model.
    """

    def describe(self, settings: FactorRiskModelSettings | None = None) -> str:

        if settings:
            n_stages = len(settings.exposures)
            if n_stages == 1:
                result = [
                    "Universe: " + str(settings.universe[0]),
                    "Exposures: " + str(settings.exposures[0]),
                    "Model Construction: " + str(settings.modelconstruction[0]),
                ]
                return os.linesep.join(result)
            else:
                result = []
                for i, (universe, exposures, modelconstruction) in enumerate(
                    zip_longest(
                        settings.universe,
                        settings.exposures,
                        settings.modelconstruction,
                        fillvalue="same as previous stage",
                    )
                ):
                    result.append(f"Stage {i + 1}:")
                    result.append("  Universe: " + str(universe))
                    result.append("  Exposures: " + str(exposures))
                    result.append("  Model Construction: " + str(modelconstruction))
                return os.linesep.join(result)
        else:
            return "This settings menu has no description."

    def validate_settings(self, settings: FactorRiskModelSettings) -> None:
        # check that the universe, exposures and model construction settings line up
        n_stages = len(settings.exposures)
        if len(settings.universe) not in (n_stages, 1):
            raise ValueError(
                f"Universe settings must be either one or {n_stages} settings."
            )
        if len(settings.modelconstruction) not in (n_stages, 1):
            raise ValueError(
                f"Model construction settings must be either one or {n_stages} settings."
            )

        modelconstruction_list = (
            settings.modelconstruction * n_stages
            if len(settings.modelconstruction) == 1
            else settings.modelconstruction
        )
        for exposures, modelconstruction in zip(
            settings.exposures, modelconstruction_list, strict=True
        ):
            if not isinstance(exposures, ExposureSettings) or not isinstance(
                modelconstruction, ModelConstructionSettings
            ):
                continue

            known_factors = set(modelconstruction.known_factors)
            other_factors = set(exposures.other)
            missing_known_exposures = known_factors - other_factors
            if missing_known_exposures:
                raise ValueError(
                    f"Invalid known factor returns: {', '.join(missing_known_exposures)}"
                )
