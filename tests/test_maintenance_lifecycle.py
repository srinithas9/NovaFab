from datetime import date

from scripts.generate_data.config import MACHINE_CONFIGS
from scripts.generate_data.health_simulator import HealthState
from scripts.generate_data.orchestrator import SimulationOrchestrator


def test_maintenance_lifecycle():
    """
    Verify that one maintenance event moves from
    IN_PROGRESS to COMPLETED without creating duplicates.
    """

    orchestrator = SimulationOrchestrator(seed=42)

    start_date = date(2026, 1, 1)

    orchestrator.initialize_machines(start_date)

    machine = MACHINE_CONFIGS[0]

    machine_code = machine.machine_code

    # Put the machine into an at-risk condition.
    health = orchestrator.machine_health[machine_code]
    health.score = 0.59
    health.state = HealthState.AT_RISK

    due_date = (
        orchestrator.next_preventive_maintenance[machine_code]
    )

    # First simulation step: maintenance should start.
    first_result = orchestrator.simulate_machine_step(
        machine,
        due_date,
    )

    first_maintenance = first_result["maintenance_record"]

    assert first_maintenance is not None
    assert first_maintenance["status"] == "IN_PROGRESS"

    assert (
        orchestrator.active_maintenance[machine_code]
        is not None
    )

    # Second simulation step: existing maintenance should complete.
    second_result = orchestrator.simulate_machine_step(
        machine,
        due_date,
    )

    second_maintenance = second_result["maintenance_record"]

    assert second_maintenance is not None
    assert second_maintenance["status"] == "COMPLETED"

    # No active maintenance should remain.
    assert (
        orchestrator.active_maintenance[machine_code]
        is None
    )

    # Health should recover.
    assert second_result["health"].score > 0.59

    # A new preventive date should be scheduled.
    assert (
        second_result["next_preventive_maintenance"]
        > due_date
    )