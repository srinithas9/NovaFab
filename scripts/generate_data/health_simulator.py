
import random

from dataclasses import dataclass
from enum import Enum


class HealthState(str, Enum):
    NORMAL = "NORMAL"
    DEGRADING = "DEGRADING"
    AT_RISK = "AT_RISK"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class MachineHealth:
    score: float = 0.95
    state: HealthState = HealthState.NORMAL


class HealthSimulator:
    """
    Simulates gradual machine health degradation and recovery.

    Health score:
        0.80 - 1.00 -> NORMAL
        0.60 - 0.80 -> DEGRADING
        below 0.60  -> AT_RISK

    Maintenance can partially restore machine health.
    """

    def __init__(
        self,
        seed: int = 42,
        degradation_rate: float = 0.0015,
        recovery_rate: float = 0.35,
    ):
        self.random = random.Random(seed)

        self.degradation_rate = degradation_rate
        self.recovery_rate = recovery_rate

    def initialize_machine(self) -> MachineHealth:
        """
        Give each machine a different starting health.
        """

        initial_score = self.random.uniform(
            0.88,
            0.98,
        )

        return MachineHealth(
            score=initial_score,
            state=self._state_from_score(
                initial_score
            ),
        )

    def update(
        self,
        health: MachineHealth,
        maintenance_completed: bool = False,
    ) -> MachineHealth:
        """
        Update machine health for one simulation day.

        Without maintenance:
            health gradually decreases.

        After completed maintenance:
            health moves toward a recovery target.
        """

        if maintenance_completed:
            health.score = self._recover(
                health.score
            )
        else:
            health.score = self._degrade(
                health.score
            )

        health.score = self._clamp(
            health.score
        )

        health.state = self._state_from_score(
            health.score
        )

        return health

    def _degrade(
        self,
        score: float,
    ) -> float:
        """
        Gradually reduce health with small randomness.
        """

        variation = self.random.uniform(
            0.75,
            1.25,
        )

        degradation = (
            self.degradation_rate
            * variation
        )

        return score - degradation

    def _recover(
        self,
        score: float,
    ) -> float:
        """
        Recover toward a healthy state after maintenance.
        """

        recovery_target = self.random.uniform(
            0.88,
            0.97,
        )

        distance_to_target = (
            recovery_target - score
        )

        return score + (
            distance_to_target
            * self.recovery_rate
        )

    @staticmethod
    def _clamp(
        score: float,
    ) -> float:
        """
        Keep health between 0 and 1.
        """

        return max(
            0.0,
            min(1.0, score),
        )

    @staticmethod
    def _state_from_score(
        score: float,
    ) -> HealthState:
        """
        Convert health score into an operational state.
        """

        if score >= 0.80:
            return HealthState.NORMAL

        if score >= 0.60:
            return HealthState.DEGRADING

        return HealthState.AT_RISK

