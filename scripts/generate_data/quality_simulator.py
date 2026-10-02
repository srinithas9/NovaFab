import random

from .config import (
    DEFECT_SEVERITIES,
    DEFECT_TYPES,
    QUALITY_RESULTS,
)
from .health_simulator import HealthState, MachineHealth


class QualitySimulator:
    """
    Generates quality inspection results and defects
    based on the current machine health state.
    """

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def generate_inspection(
        self,
        health: MachineHealth,
        rejected_quantity: int,
    ) -> dict:
        result = self._generate_result(health.state)

        defect_count = self._generate_defect_count(
            health.state,
            rejected_quantity,
            result,
        )

        defects = self._generate_defects(
            defect_count,
            health.state,
        )

        return {
            "result": result,
            "defect_count": defect_count,
            "defects": defects,
        }

    def _generate_result(
        self,
        health_state: HealthState,
    ) -> str:
        if health_state == HealthState.NORMAL:
            weights = [0.90, 0.08, 0.02]

        elif health_state == HealthState.DEGRADING:
            weights = [0.70, 0.20, 0.10]

        elif health_state == HealthState.AT_RISK:
            weights = [0.45, 0.30, 0.25]

        else:
            weights = [0.90, 0.08, 0.02]

        return self.random.choices(
            QUALITY_RESULTS,
            weights=weights,
            k=1,
        )[0]

    def _generate_defect_count(
        self,
        health_state: HealthState,
        rejected_quantity: int,
        result: str,
    ) -> int:
        if result == "PASS":
            return 0

        if rejected_quantity == 0:
            return 0

        if health_state == HealthState.NORMAL:
            maximum = min(rejected_quantity, 2)

        elif health_state == HealthState.DEGRADING:
            maximum = min(rejected_quantity, 5)

        else:
            maximum = min(rejected_quantity, 10)

        if maximum <= 0:
            return 0

        return self.random.randint(1, maximum)

    def _generate_defects(
        self,
        defect_count: int,
        health_state: HealthState,
    ) -> list[dict]:
        defects = []

        for _ in range(defect_count):
            defects.append(
                {
                    "defect_type": self._generate_defect_type(),
                    "severity": self._generate_severity(
                        health_state
                    ),
                    "description": self._generate_description(
                        health_state
                    ),
                }
            )

        return defects

    def _generate_defect_type(self) -> str:
        return self.random.choice(DEFECT_TYPES)

    def _generate_severity(
        self,
        health_state: HealthState,
    ) -> str:
        if health_state == HealthState.NORMAL:
            weights = [0.70, 0.25, 0.05, 0.00]

        elif health_state == HealthState.DEGRADING:
            weights = [0.45, 0.35, 0.17, 0.03]

        elif health_state == HealthState.AT_RISK:
            weights = [0.20, 0.35, 0.30, 0.15]

        else:
            weights = [0.70, 0.25, 0.05, 0.00]

        return self.random.choices(
            DEFECT_SEVERITIES,
            weights=weights,
            k=1,
        )[0]

    def _generate_description(
        self,
        health_state: HealthState,
    ) -> str:
        if health_state == HealthState.NORMAL:
            descriptions = [
                "Minor production variation detected.",
                "Small surface or dimensional deviation observed.",
            ]

        elif health_state == HealthState.DEGRADING:
            descriptions = [
                "Increased production variation detected.",
                "Inspection identified a recurring quality deviation.",
                "Machine condition may be contributing to the defect.",
            ]

        else:
            descriptions = [
                "Significant quality deviation detected.",
                "Inspection identified a severe production defect.",
                "Machine condition is likely contributing to the defect.",
            ]

        return self.random.choice(descriptions)