import random

from .config import MachineConfig
from .health_simulator import HealthState, MachineHealth


class ProductionSimulator:
    """
    Generates production-run outcomes based on machine configuration
    and current machine health.
    """

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def generate_run(
        self,
        machine_config: MachineConfig,
        health: MachineHealth,
    ) -> dict:
        target_quantity = self._generate_target_quantity(machine_config)

        efficiency = self._generate_efficiency(health.state)

        produced_quantity = int(target_quantity * efficiency)

        rejection_rate = self._generate_rejection_rate(health.state)

        rejected_quantity = int(
            produced_quantity * rejection_rate
        )

        return {
            "target_quantity": target_quantity,
            "produced_quantity": produced_quantity,
            "rejected_quantity": rejected_quantity,
        }

    def _generate_target_quantity(
        self,
        config: MachineConfig,
    ) -> int:
        return self.random.randint(
            config.production_min,
            config.production_max,
        )

    def _generate_efficiency(
        self,
        health_state: HealthState,
    ) -> float:
        if health_state == HealthState.NORMAL:
            minimum, maximum = 0.90, 1.00

        elif health_state == HealthState.DEGRADING:
            minimum, maximum = 0.80, 0.95

        elif health_state == HealthState.AT_RISK:
            minimum, maximum = 0.60, 0.85

        else:
            minimum, maximum = 0.90, 1.00

        return self.random.uniform(minimum, maximum)

    def _generate_rejection_rate(
        self,
        health_state: HealthState,
    ) -> float:
        if health_state == HealthState.NORMAL:
            minimum, maximum = 0.01, 0.03

        elif health_state == HealthState.DEGRADING:
            minimum, maximum = 0.02, 0.06

        elif health_state == HealthState.AT_RISK:
            minimum, maximum = 0.05, 0.15

        else:
            minimum, maximum = 0.01, 0.03

        return self.random.uniform(minimum, maximum)