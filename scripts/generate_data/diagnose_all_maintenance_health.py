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

    maintenance_events = []

    current_date = SIMULATION_START

    while current_date <= SIMULATION_END:
        for machine in MACHINE_CONFIGS:
            machine_code = machine.machine_code

            # Capture health BEFORE the simulation step.
            health_before = orchestrator.machine_health[
                machine_code
            ]

            health_score_before = health_before.score
            health_state_before = health_before.state.value

            result = orchestrator.simulate_machine_step(
                machine,
                current_date,
            )

            maintenance = result["maintenance_record"]

            if maintenance is not None:
                maintenance_events.append(
                    {
                        "date": current_date,
                        "machine": machine_code,
                        "type": maintenance["maintenance_type"],
                        "health_before": health_score_before,
                        "state_before": health_state_before,
                        "health_after": result["health"].score,
                        "state_after": result["health"].state.value,
                    }
                )

        current_date += timedelta(days=1)

    print()
    print("MAINTENANCE EVENTS — HEALTH BEFORE VS AFTER")
    print("=" * 100)

    for event in maintenance_events:
        print(
            f"{event['date']} | "
            f"{event['machine']:8} | "
            f"{event['type']:10} | "
            f"BEFORE={event['health_before']:.3f} "
            f"({event['state_before']:9}) | "
            f"AFTER={event['health_after']:.3f} "
            f"({event['state_after']})"
        )

    print()
    print("SUMMARY BY MAINTENANCE TYPE — HEALTH BEFORE")
    print("=" * 100)

    maintenance_types = {}

    for event in maintenance_events:
        maintenance_types.setdefault(
            event["type"],
            [],
        ).append(event["health_before"])

    for maintenance_type, health_values in sorted(
        maintenance_types.items()
    ):
        print(
            f"{maintenance_type:10} | "
            f"count={len(health_values):3} | "
            f"min={min(health_values):.3f} | "
            f"max={max(health_values):.3f} | "
            f"avg={sum(health_values) / len(health_values):.3f}"
        )


if __name__ == "__main__":
    main()