from datetime import timedelta

from .config import (
    MACHINE_CONFIGS,
    RANDOM_SEED,
    SIMULATION_START,
    SIMULATION_END,
)
from .orchestrator import SimulationOrchestrator


def main():
    orchestrator = SimulationOrchestrator(seed=RANDOM_SEED)
    orchestrator.initialize_machines(SIMULATION_START)

    corrective_events = []
    seen_events = set()

    current_date = SIMULATION_START

    while current_date <= SIMULATION_END:
        for machine_config in MACHINE_CONFIGS:
            result = orchestrator.simulate_machine_step(
                machine_config,
                current_date,
            )

            maintenance = result["maintenance_record"]

            if (
                maintenance is not None
                and maintenance["maintenance_type"] == "CORRECTIVE"
            ):
                event_key = (
                    machine_config.machine_code,
                    maintenance["scheduled_date"],
                )

                if event_key not in seen_events:
                    seen_events.add(event_key)

                    health = result["health"]

                    corrective_events.append(
                        {
                            "machine_code": machine_config.machine_code,
                            "date": current_date,
                            "health_score": health.score,
                            "health_state": health.state.value,
                        }
                    )

        current_date += timedelta(days=1)

    print("\nCORRECTIVE MAINTENANCE HEALTH")
    print("=" * 70)

    for event in corrective_events:
        print(
            f"{event['date']} | "
            f"{event['machine_code']:8} | "
            f"health={event['health_score']:.3f} | "
            f"state={event['health_state']}"
        )

    print("\nSummary")
    print("=" * 70)

    print(f"Corrective events: {len(corrective_events)}")

    if corrective_events:
        scores = [
            event["health_score"]
            for event in corrective_events
        ]

        normal = sum(
            event["health_state"] == "NORMAL"
            for event in corrective_events
        )

        degrading = sum(
            event["health_state"] == "DEGRADING"
            for event in corrective_events
        )

        at_risk = sum(
            event["health_state"] == "AT_RISK"
            for event in corrective_events
        )

        print(f"Normal:      {normal}")
        print(f"Degrading:   {degrading}")
        print(f"At risk:     {at_risk}")
        print(f"Minimum health: {min(scores):.3f}")
        print(f"Maximum health: {max(scores):.3f}")
        print(f"Average health: {sum(scores) / len(scores):.3f}")


if __name__ == "__main__":
    main()