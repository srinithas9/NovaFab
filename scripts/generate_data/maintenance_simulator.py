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

    Preventive maintenance is calendar-driven.

    Corrective maintenance is condition-driven:
    as machine health deteriorates, the probability of
    corrective maintenance increases significantly.
    """

    def __init__(
        self,
        seed: int = 42,
        corrective_probability: float = 0.001,
    ):
        self.random = random.Random(seed)
        self.corrective_probability = corrective_probability

    def get_next_preventive_date(
        self,
        current_date: date,
    ) -> date:
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
        The probability increases sharply as machine
        health deteriorates.
        """

        if current_date >= next_preventive_date:
            return True

        corrective_probability = (
            self._get_corrective_probability(
                machine_health.score
            )
        )

        return (
            self.random.random()
            < corrective_probability
        )

    def _get_corrective_probability(
        self,
        health_score: float,
    ) -> float:
        """
        Return the daily probability of corrective maintenance
        based on the current machine health score.

        Corrective risk increases as machine health deteriorates.

        Health score:
            >= 0.85 -> very low corrective risk
            0.80-0.85 -> low corrective risk
            0.75-0.80 -> elevated corrective risk
            0.70-0.75 -> high corrective risk
            0.60-0.70 -> very high corrective risk
            < 0.60 -> critical corrective risk
        """

        if health_score >= 0.85:
            return self.corrective_probability

        if health_score >= 0.80:
            return 0.010

        if health_score >= 0.75:
            return 0.100

        if health_score >= 0.70:
            return 0.250

        if health_score >= 0.60:
            return 0.400

        return 0.600

    def generate_record(
        self,
        machine_health: MachineHealth,
        scheduled_date: date,
        preventive_due: bool = False,
    ) -> dict:
        maintenance_type = self._generate_type(
            machine_health.state,
            preventive_due,
        )

        status = self._generate_status(
            machine_health.state,
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
                [
                    "CORRECTIVE",
                    "CORRECTIVE",
                    "INSPECTION",
                ]
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
                MAINTENANCE_TYPE_WEIGHTS[t]
                for t in MAINTENANCE_TYPES
            ],
            k=1,
        )[0]

    def _generate_status(
        self,
        health_state: HealthState,
    ) -> str:
        if health_state == HealthState.AT_RISK:
            return self.random.choice(
                [
                    "IN_PROGRESS",
                    "COMPLETED",
                ]
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