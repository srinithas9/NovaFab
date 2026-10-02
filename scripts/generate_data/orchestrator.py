
from datetime import date, datetime, time

from .config import MACHINE_CONFIGS, RANDOM_SEED
from .health_simulator import HealthSimulator, MachineHealth
from .sensor_simulator import SensorSimulator
from .production_simulator import ProductionSimulator
from .quality_simulator import QualitySimulator
from .maintenance_simulator import MaintenanceSimulator


class SimulationOrchestrator:
    """
    Coordinates the individual simulation components.

    Machine health persists across simulation steps.

    Continuous events:
        - sensor readings
        - production runs
        - quality inspections

    Event-driven processes:
        - maintenance

    Sensor readings are generated every 15 minutes
    during the 8-hour production shift.

    Only one maintenance event can be active for a machine
    at any given time.

    Completed maintenance can improve machine health.
    """

    def __init__(self, seed: int = RANDOM_SEED):
        self.health_simulator = HealthSimulator(seed=seed)
        self.sensor_simulator = SensorSimulator(seed=seed)
        self.production_simulator = ProductionSimulator(seed=seed)
        self.quality_simulator = QualitySimulator(seed=seed)
        self.maintenance_simulator = MaintenanceSimulator(seed=seed)

        self.machine_health: dict[str, MachineHealth] = {}

        self.next_preventive_maintenance: dict[str, date] = {}

        self.active_maintenance: dict[str, dict | None] = {}

    def initialize_machines(
        self,
        start_date: date,
    ) -> None:
        """
        Initialize health and preventive maintenance
        schedules for every machine.
        """

        for machine_config in MACHINE_CONFIGS:
            machine_code = machine_config.machine_code

            self.machine_health[machine_code] = (
                self.health_simulator.initialize_machine()
            )

            self.next_preventive_maintenance[machine_code] = (
                self.maintenance_simulator.get_next_preventive_date(
                    start_date
                )
            )

            self.active_maintenance[machine_code] = None

    def simulate_machine_step(
        self,
        machine_config,
        simulation_date: date,
    ) -> dict:
        """
        Simulate one machine for one production day.

        The daily machine state controls:
            - machine health
            - production
            - quality
            - maintenance

        Sensor data is generated at 15-minute intervals
        throughout the 8-hour production shift.
        """

        machine_code = machine_config.machine_code

        # ---------------------------------------------------------
        # 1. Initialize machine state if necessary
        # ---------------------------------------------------------

        if machine_code not in self.machine_health:
            self.machine_health[machine_code] = (
                self.health_simulator.initialize_machine()
            )

        if machine_code not in self.next_preventive_maintenance:
            self.next_preventive_maintenance[machine_code] = (
                self.maintenance_simulator.get_next_preventive_date(
                    simulation_date
                )
            )

        if machine_code not in self.active_maintenance:
            self.active_maintenance[machine_code] = None

        health = self.machine_health[machine_code]

        next_preventive_date = (
            self.next_preventive_maintenance[machine_code]
        )

        active_maintenance = (
            self.active_maintenance[machine_code]
        )

        maintenance_record = None
        maintenance_completed = False

        # ---------------------------------------------------------
        # 2. Continue an existing maintenance event
        # ---------------------------------------------------------

        if active_maintenance is not None:

            maintenance_record = active_maintenance

            if active_maintenance["status"] == "IN_PROGRESS":
                # Complete the active maintenance event
                # on the next simulation step.
                active_maintenance["status"] = "COMPLETED"
                active_maintenance["completed_date"] = simulation_date

                maintenance_completed = True

            elif active_maintenance["status"] == "SCHEDULED":
                # Move scheduled maintenance into progress.
                active_maintenance["status"] = "IN_PROGRESS"

        # ---------------------------------------------------------
        # 3. Create a new maintenance event only when
        #    no maintenance event is currently active
        # ---------------------------------------------------------

        else:

            maintenance_due = (
                self.maintenance_simulator.should_schedule_maintenance(
                    health,
                    simulation_date,
                    next_preventive_date,
                )
            )

            if maintenance_due:

                preventive_due = (
                    simulation_date >= next_preventive_date
                )

                maintenance_record = (
                    self.maintenance_simulator.generate_record(
                        health,
                        simulation_date,
                        preventive_due=preventive_due,
                    )
                )

                self.active_maintenance[machine_code] = (
                    maintenance_record
                )

                if maintenance_record["status"] == "COMPLETED":
                    maintenance_completed = True

        # ---------------------------------------------------------
        # 4. Handle completed maintenance
        # ---------------------------------------------------------

        if maintenance_completed:

            self.active_maintenance[machine_code] = None

            self.next_preventive_maintenance[machine_code] = (
                self.maintenance_simulator.get_next_preventive_date(
                    simulation_date
                )
            )

        # ---------------------------------------------------------
        # 5. Update machine health
        # ---------------------------------------------------------

        self.health_simulator.update(
            health,
            maintenance_completed=maintenance_completed,
        )

        # ---------------------------------------------------------
        # 6. Generate 15-minute sensor data
        # ---------------------------------------------------------

        shift_start = datetime.combine(
            simulation_date,
            time(8, 0),
        )

        sensor_readings = (
            self.sensor_simulator.generate_shift_readings(
                machine_config,
                health,
                shift_start,
                duration_hours=8,
            )
        )

        # ---------------------------------------------------------
        # 7. Generate production data
        # ---------------------------------------------------------

        production_run = self.production_simulator.generate_run(
            machine_config,
            health,
        )

        # ---------------------------------------------------------
        # 8. Generate quality data
        # ---------------------------------------------------------

        quality_inspection = (
            self.quality_simulator.generate_inspection(
                health,
                production_run["rejected_quantity"],
            )
        )

        # ---------------------------------------------------------
        # 9. Return complete simulation result
        # ---------------------------------------------------------

        return {
            "machine_code": machine_code,
            "date": simulation_date,
            "health": health,
            "sensor_readings": sensor_readings,
            "production_run": production_run,
            "quality_inspection": quality_inspection,
            "maintenance_record": maintenance_record,
            "next_preventive_maintenance": (
                self.next_preventive_maintenance[machine_code]
            ),
        }

