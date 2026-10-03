from datetime import timedelta

from scripts.generate_data.config import (
    MACHINE_CONFIGS,
    SIMULATION_START,
    SIMULATION_END,
)
from scripts.generate_data.orchestrator import SimulationOrchestrator


def main():
    orchestrator = SimulationOrchestrator()
    orchestrator.initialize_machines(SIMULATION_START)

    minimum_health = {
        machine.machine_code: 1.0
        for machine in MACHINE_CONFIGS
    }

    minimum_date = {
        machine.machine_code: None
        for machine in MACHINE_CONFIGS
    }

    maximum_health = {
        machine.machine_code: 0.0
        for machine in MACHINE_CONFIGS
    }

    current_date = SIMULATION_START

    while current_date <= SIMULATION_END:
        for machine in MACHINE_CONFIGS:
            result = orchestrator.simulate_machine_step(
                machine,
                current_date,
            )

            health = result["health"].score
            machine_code = machine.machine_code

            if health < minimum_health[machine_code]:
                minimum_health[machine_code] = health
                minimum_date[machine_code] = current_date

            if health > maximum_health[machine_code]:
                maximum_health[machine_code] = health

        current_date += timedelta(days=1)

    print()
    print("MACHINE HEALTH RANGE")
    print("=" * 70)

    for machine in MACHINE_CONFIGS:
        machine_code = machine.machine_code

        print(
            f"{machine_code:8} | "
            f"min={minimum_health[machine_code]:.3f} "
            f"({minimum_date[machine_code]}) | "
            f"max={maximum_health[machine_code]:.3f}"
        )


if __name__ == "__main__":
    main()