import os
from typing import Literal, Mapping

from pydantic import Field, NonNegativeFloat, field_validator

from bayesline.api._src.registry import Settings, SettingsMenu

WeightingScheme = Literal["SqrtCap", "InvIdioVar"]


class ModelConstructionSettings(Settings):
    """
    Defines settings to build a factor risk model.
    """

    @classmethod
    def default(cls) -> "ModelConstructionSettings":
        return cls(weights="SqrtCap")

    currency: str = Field(
        description="The currency of the factor risk model.",
        default="USD",
        examples=["USD", "EUR"],
    )
    weights: WeightingScheme = Field(
        description="The regression weights used for the factor risk model.",
        default="SqrtCap",
        examples=["SqrtCap", "InvIdioVar"],
    )
    alpha: NonNegativeFloat = Field(
        description="The ridge-shrinkage factor for the factor risk model.",
        default=0.0,
    )
    alpha_overrides: dict[str, NonNegativeFloat] = Field(
        description=(
            "The alpha override for the factor risk model. The keys are the factor "
            "names and the values are the alpha overrides."
        ),
        default_factory=dict,
    )
    return_clip_bounds: tuple[float | None, float | None] = Field(
        description="The bounds for the return clipping.",
        default=(-0.1, 0.1),
        examples=[(-0.1, 0.1), (None, None)],
    )
    known_factors: Mapping[str, str] = Field(
        description=(
            "The known factor returns to use for the factor risk model which are added "
            "as independent factors with known (constrained) values. "
            "The keys are the names that should be used in the factor model and the "
            "values are the underlying known factors that should be used. "
        ),
        default_factory=dict,
        examples=[{}, {"Risk Free Rate": "us_rate_3m"}],
    )

    @field_validator("return_clip_bounds")
    @classmethod
    def return_clip_bounds_valid(
        cls, v: tuple[float | None, float | None]
    ) -> tuple[float | None, float | None]:
        lb, ub = v
        if lb is not None and ub is not None and ub < lb:
            raise ValueError(f"Lower bound {lb} cannot be bigger than upper bound {ub}")
        return v


class ModelConstructionSettingsMenu(
    SettingsMenu[ModelConstructionSettings], frozen=True, extra="forbid"
):
    """
    Defines available modelconstruction settings to build a factor risk model.
    """

    weights: list[WeightingScheme] = Field(
        description="""
        The available regression weights that can be used for the factor risk model.
        """,
    )

    known_factors: dict[str, str] = Field(
        description="""
        The available known factor returns that can be used for the factor risk model.
        The keys are the factor names and the values a description for this known factor.
        """,
    )

    def describe(self, settings: ModelConstructionSettings | None = None) -> str:
        if settings is not None:
            known_factors = []
            for factor, value in settings.known_factors.items():
                known_factors.append(f"{factor}: {value}")
            out = f"Weights: {settings.weights}"
            if known_factors:
                out += os.linesep
                out += f"Known Factors: {', '.join(known_factors)}"
            return out
        else:
            known_factors = []
            for factor, desc in self.known_factors.items():
                known_factors.append(f"  - {factor}: {desc}")
            out = f"Weights: {', '.join(self.weights)}"
            if known_factors:
                out += os.linesep
                out += f"Known Factors:{os.linesep}{os.linesep.join(known_factors)}"
            return out

    def validate_settings(self, settings: ModelConstructionSettings) -> None:
        if settings.weights not in self.weights:
            raise ValueError(f"Invalid weights: {settings.weights}")

        missing_known_factors = set(settings.known_factors.values()) - set(
            self.known_factors.keys()
        )
        if missing_known_factors:
            raise ValueError(
                f"Invalid known factor returns: {', '.join(missing_known_factors)}"
            )
