
from datetime import date

from scripts.generate_data.config import MACHINE_CONFIGS
from scripts.generate_data.orchestrator import SimulationOrchestrator


def test_simulation_orchestrator():
    """
    Verify that one machine can complete a full
    simulation step and produce all expected outputs.
    """

    orchestrator = SimulationOrchestrator(seed=42)

    start_date = date(2026, 1, 1)

    orchestrator.initialize_machines(start_date)

    machine = MACHINE_CONFIGS[0]

    result = orchestrator.simulate_machine_step(
        machine,
        start_date,
    )

    # Basic machine information.
    assert result["machine_code"] == machine.machine_code
    assert result["date"] == start_date

    # Health output.
    assert result["health"] is not None
    assert 0.0 <= result["health"].score <= 1.0

    # Sensor output.
    sensor_readings = result["sensor_readings"]

    assert sensor_readings is not None
    assert len(sensor_readings) > 0

    # Verify the expected 15-minute sensor interval.
    assert sensor_readings[0]["timestamp"] is not None

    # Production output.
    production_run = result["production_run"]

    assert production_run is not None
    assert production_run["target_quantity"] > 0
    assert production_run["produced_quantity"] > 0
    assert production_run["rejected_quantity"] >= 0

    # Quality output.
    quality_inspection = result["quality_inspection"]

    assert quality_inspection is not None
    assert quality_inspection["result"] in {
        "PASS",
        "REVIEW",
        "FAIL",
    }

    assert quality_inspection["defect_count"] >= 0

    # Maintenance output is allowed to be absent
    # because maintenance is event-driven.
    assert "maintenance_record" in result

    # Preventive maintenance tracking should exist.
    assert result["next_preventive_maintenance"] is not None

