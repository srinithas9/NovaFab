
from datetime import datetime, time, timedelta
from pathlib import Path

from .config import (
    FACTORY_CONFIG,
    MACHINE_CONFIGS,
    SIMULATION_START,
    SIMULATION_END,
)
from .csv_writer import write_csv
from .orchestrator import SimulationOrchestrator


RAW_DATA_DIR = Path("data/raw")

# Factory production shift.
SHIFT_START_HOUR = 8
SHIFT_DURATION_HOURS = 8


def build_factory_rows():
    """
    Convert factory configuration into raw factory records.
    """

    return [
        {
            "factory_code": FACTORY_CONFIG["factory_code"],
            "name": FACTORY_CONFIG["name"],
            "location": FACTORY_CONFIG["location"],
            "industry": FACTORY_CONFIG["industry"],
        }
    ]


def build_machine_rows():
    """
    Convert machine configuration into raw machine records.
    """

    return [
        {
            "machine_code": machine.machine_code,
            "factory_code": FACTORY_CONFIG["factory_code"],
            "name": machine.name,
            "machine_type": machine.machine_type,
            "installation_date": "2024-01-01",
            "is_active": True,
        }
        for machine in MACHINE_CONFIGS
    ]


def run_simulation():
    """
    Run the factory simulation across all configured machines
    and simulation dates.

    Each machine-day produces:
        - multiple sensor readings during the shift
        - one production run
        - one quality inspection
        - zero or one maintenance event/lifecycle update
    """

    orchestrator = SimulationOrchestrator()

    orchestrator.initialize_machines(SIMULATION_START)

    simulation_date = SIMULATION_START

    results = []

    while simulation_date <= SIMULATION_END:
        for machine_config in MACHINE_CONFIGS:
            result = orchestrator.simulate_machine_step(
                machine_config,
                simulation_date,
            )

            results.append(result)

        simulation_date += timedelta(days=1)

    return results


def build_sensor_rows(results):
    """
    Convert 15-minute sensor readings from simulation results
    into raw sensor records.

    The production shift runs from 08:00 to 16:00.

    With a 15-minute interval:
        8 hours × 4 readings/hour = 32 readings
        per machine per production day.
    """

    rows = []

    for result in results:
        sensor_readings = result["sensor_readings"]

        for sensor in sensor_readings:
            rows.append(
                {
                    "machine_code": result["machine_code"],
                    "timestamp": sensor["timestamp"],
                    "temperature": sensor["temperature"],
                    "vibration": sensor["vibration"],
                    "pressure": sensor["pressure"],
                    "power_consumption": sensor["power_consumption"],
                }
            )

    return rows


def build_production_rows(results):
    """
    Convert simulation results into production run rows.

    Each simulated machine-day represents one production shift.

    The shift runs from 08:00 to 16:00.
    """

    rows = []

    for result in results:
        production = result["production_run"]

        simulation_date = result["date"]

        start_time = datetime.combine(
            simulation_date,
            time(SHIFT_START_HOUR, 0),
        )

        end_time = start_time + timedelta(
            hours=SHIFT_DURATION_HOURS
        )

        rows.append(
            {
                "machine_code": result["machine_code"],
                "product_code": "PROD-A",
                "batch_number": (
                    f"BATCH-{result['machine_code']}-{result['date']}"
                ),
                "start_time": start_time,
                "end_time": end_time,
                "target_quantity": production["target_quantity"],
                "produced_quantity": production["produced_quantity"],
                "rejected_quantity": production["rejected_quantity"],
            }
        )

    return rows


def build_quality_rows(results):
    """
    Convert simulation results into quality inspection rows.
    """

    rows = []

    for result in results:
        quality = result["quality_inspection"]

        rows.append(
            {
                "machine_code": result["machine_code"],
                "batch_number": (
                    f"BATCH-{result['machine_code']}-{result['date']}"
                ),
                "inspection_time": result["date"],
                "result": quality["result"],
                "defect_count": quality["defect_count"],
            }
        )

    return rows


def build_defect_rows(results):
    """
    Convert individual defects from quality inspections
    into raw defect records.
    """

    rows = []

    for result in results:
        quality = result["quality_inspection"]

        batch_number = (
            f"BATCH-{result['machine_code']}-{result['date']}"
        )

        for defect in quality["defects"]:
            rows.append(
                {
                    "batch_number": batch_number,
                    "defect_type": defect["defect_type"],
                    "severity": defect["severity"],
                    "description": defect["description"],
                }
            )

    return rows


def build_maintenance_rows(results):
    """
    Convert maintenance events from simulation results
    into unique raw maintenance records.

    A maintenance event may appear in multiple simulation steps
    while moving through its lifecycle. Each maintenance episode
    should therefore be exported only once.
    """

    rows = []

    exported_events = set()

    for result in results:
        maintenance = result["maintenance_record"]

        if maintenance is None:
            continue

        event_key = (
            result["machine_code"],
            maintenance["scheduled_date"],
            maintenance["maintenance_type"],
        )

        if event_key in exported_events:
            continue

        exported_events.add(event_key)

        rows.append(
            {
                "machine_code": result["machine_code"],
                "maintenance_type": maintenance["maintenance_type"],
                "status": maintenance["status"],
                "scheduled_date": maintenance["scheduled_date"],
                "completed_date": maintenance["completed_date"],
                "description": maintenance["description"],
                "technician_notes": maintenance["technician_notes"],
            }
        )

    return rows


def generate_raw_data():
    """
    Generate and persist the raw factory datasets.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # Master data
    # ---------------------------------------------------------

    write_csv(
        RAW_DATA_DIR / "factories.csv",
        build_factory_rows(),
        [
            "factory_code",
            "name",
            "location",
            "industry",
        ],
    )

    write_csv(
        RAW_DATA_DIR / "machines.csv",
        build_machine_rows(),
        [
            "machine_code",
            "factory_code",
            "name",
            "machine_type",
            "installation_date",
            "is_active",
        ],
    )

    # ---------------------------------------------------------
    # Simulation
    # ---------------------------------------------------------

    results = run_simulation()

    # ---------------------------------------------------------
    # Sensor data
    # ---------------------------------------------------------

    sensor_rows = build_sensor_rows(results)

    write_csv(
        RAW_DATA_DIR / "sensor_readings.csv",
        sensor_rows,
        [
            "machine_code",
            "timestamp",
            "temperature",
            "vibration",
            "pressure",
            "power_consumption",
        ],
    )

    # ---------------------------------------------------------
    # Production data
    # ---------------------------------------------------------

    production_rows = build_production_rows(results)

    write_csv(
        RAW_DATA_DIR / "production_runs.csv",
        production_rows,
        [
            "machine_code",
            "product_code",
            "batch_number",
            "start_time",
            "end_time",
            "target_quantity",
            "produced_quantity",
            "rejected_quantity",
        ],
    )

    # ---------------------------------------------------------
    # Quality data
    # ---------------------------------------------------------

    quality_rows = build_quality_rows(results)

    write_csv(
        RAW_DATA_DIR / "quality_inspections.csv",
        quality_rows,
        [
            "machine_code",
            "batch_number",
            "inspection_time",
            "result",
            "defect_count",
        ],
    )

    # ---------------------------------------------------------
    # Defect data
    # ---------------------------------------------------------

    defect_rows = build_defect_rows(results)

    write_csv(
        RAW_DATA_DIR / "defects.csv",
        defect_rows,
        [
            "batch_number",
            "defect_type",
            "severity",
            "description",
        ],
    )

    # ---------------------------------------------------------
    # Maintenance data
    # ---------------------------------------------------------

    maintenance_rows = build_maintenance_rows(results)

    write_csv(
        RAW_DATA_DIR / "maintenance_records.csv",
        maintenance_rows,
        [
            "machine_code",
            "maintenance_type",
            "status",
            "scheduled_date",
            "completed_date",
            "description",
            "technician_notes",
        ],
    )

    return results


if __name__ == "__main__":
    results = generate_raw_data()

    sensor_count = sum(
        len(result["sensor_readings"])
        for result in results
    )

    print("Simulation completed.")
    print(f"Simulation start: {SIMULATION_START}")
    print(f"Simulation end: {SIMULATION_END}")
    print(f"Machines: {len(MACHINE_CONFIGS)}")
    print(f"Simulation results: {len(results)}")
    print(f"Sensor readings: {sensor_count}")

    print("Generated:")
    print("  - data/raw/factories.csv")
    print("  - data/raw/machines.csv")
    print("  - data/raw/sensor_readings.csv")
    print("  - data/raw/production_runs.csv")
    print("  - data/raw/quality_inspections.csv")
    print("  - data/raw/defects.csv")
    print("  - data/raw/maintenance_records.csv")

