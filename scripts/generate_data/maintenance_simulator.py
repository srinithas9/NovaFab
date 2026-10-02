import random
from datetime import date, timedelta

from .config import (
    MAINTENANCE_STATUSES,
    MAINTENANCE_TYPES,
    MAINTENANCE_TYPE_WEIGHTS,
    PREVENTIVE_MAINTENANCE_DAYS,
)
from .health_simulator import HealthState, MachineHealth


class MaintenanceSimulator:
    """
    Generates maintenance events based on scheduled dates
    and machine health conditions.
    """

    def __init__(
        self,
        seed: int = 42,
        corrective_probability: float = 0.01,
    ):
        self.random = random.Random(seed)
        self.corrective_probability = corrective_probability

    def get_next_preventive_date(
        self,
        current_date: date,
    ) -> date:
        """
        Schedule the next preventive maintenance date.

        The interval is randomly selected from the configured
        preventive-maintenance range.
        """

        minimum_days, maximum_days = PREVENTIVE_MAINTENANCE_DAYS

        interval_days = self.random.randint(
            minimum_days,
            maximum_days,
        )

        return current_date + timedelta(
            days=interval_days
        )

    def should_schedule_maintenance(
        self,
        machine_health: MachineHealth,
        current_date: date,
        next_preventive_date: date,
    ) -> bool:
        """
        Determine whether maintenance should occur.

        Preventive maintenance is date-driven.

        Corrective maintenance is condition-driven.
        """

        # Preventive maintenance is due.
        if current_date >= next_preventive_date:
            return True

        # At-risk machines can require corrective maintenance
        # before their preventive date.
        if machine_health.state == HealthState.AT_RISK:
            return self.random.random() < 0.10

        # Degrading machines have a smaller chance of
        # requiring corrective intervention.
        if machine_health.state == HealthState.DEGRADING:
            return self.random.random() < 0.03

        # Healthy machines rarely need unexpected maintenance.
        return self.random.random() < self.corrective_probability

    def generate_record(
        self,
        machine_health: MachineHealth,
        scheduled_date: date,
        preventive_due: bool = False,
    ) -> dict:
        """
        Generate one maintenance record.
        """

        maintenance_type = self._generate_type(
            machine_health.state,
            preventive_due,
        )

        status = self._generate_status(
            machine_health.state
        )

        completed_date = self._generate_completed_date(
            scheduled_date,
            status,
        )

        description = self._generate_description(
            maintenance_type,
            machine_health.state,
        )

        technician_notes = self._generate_technician_notes(
            machine_health.state,
            maintenance_type,
        )

        return {
            "maintenance_type": maintenance_type,
            "status": status,
            "scheduled_date": scheduled_date,
            "completed_date": completed_date,
            "description": description,
            "technician_notes": technician_notes,
        }

    def _generate_type(
        self,
        health_state: HealthState,
        preventive_due: bool,
    ) -> str:
        if preventive_due:
            return "PREVENTIVE"

        if health_state == HealthState.AT_RISK:
            return self.random.choice(
                ["CORRECTIVE", "CORRECTIVE", "INSPECTION"]
            )

        if health_state == HealthState.DEGRADING:
            return self.random.choice(
                [
                    "PREVENTIVE",
                    "PREVENTIVE",
                    "CORRECTIVE",
                    "INSPECTION",
                ]
            )

        return self.random.choices(
            MAINTENANCE_TYPES,
            weights=[
                MAINTENANCE_TYPE_WEIGHTS[
                    maintenance_type
                ]
                for maintenance_type in MAINTENANCE_TYPES
            ],
            k=1,
        )[0]

    def _generate_status(
        self,
        health_state: HealthState,
    ) -> str:
        if health_state == HealthState.AT_RISK:
            return self.random.choice(
                ["IN_PROGRESS", "COMPLETED"]
            )

        return self.random.choices(
            MAINTENANCE_STATUSES,
            weights=[0.10, 0.10, 0.80],
            k=1,
        )[0]

    def _generate_completed_date(
        self,
        scheduled_date: date,
        status: str,
    ) -> date | None:
        if status != "COMPLETED":
            return None

        completion_days = self.random.randint(0, 3)

        return scheduled_date + timedelta(
            days=completion_days
        )

    def _generate_description(
        self,
        maintenance_type: str,
        health_state: HealthState,
    ) -> str:
        if maintenance_type == "PREVENTIVE":
            return (
                "Routine preventive maintenance performed "
                "to maintain machine operating condition."
            )

        if maintenance_type == "CORRECTIVE":
            if health_state == HealthState.AT_RISK:
                return (
                    "Corrective maintenance performed after "
                    "significant abnormal machine behavior."
                )

            return (
                "Corrective maintenance performed following "
                "abnormal machine behavior."
            )

        return (
            "Machine inspection performed to assess "
            "operating condition."
        )

    def _generate_technician_notes(
        self,
        health_state: HealthState,
        maintenance_type: str,
    ) -> str:
        if maintenance_type == "PREVENTIVE":
            notes = [
                "Routine maintenance completed successfully.",
                "Machine operating within expected range.",
                "Preventive service completed as scheduled.",
            ]

        elif maintenance_type == "CORRECTIVE":
            if health_state == HealthState.AT_RISK:
                notes = [
                    "Abnormal machine condition identified.",
                    "Corrective action required.",
                    "Machine condition requires close monitoring.",
                ]
            else:
                notes = [
                    "Early signs of machine degradation observed.",
                    "Abnormal behavior investigated.",
                    "Sensor readings should be monitored.",
                ]

        else:
            notes = [
                "Machine condition inspected.",
                "Additional monitoring recommended.",
                "Inspection completed without major findings.",
            ]

        return self.random.choice(notes)