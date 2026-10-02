
import random

from .config import (
    SENSOR_ANOMALY_RATE,
    SENSOR_INTERVAL_MINUTES,
    SENSOR_MISSING_RATE,
    MachineConfig,
)
from .health_simulator import HealthState, MachineHealth


class SensorSimulator:
    """
    Generates time-series sensor readings based on machine health.

    Sensor readings are generated at a fixed interval during the
    production shift.

    The machine health state controls the expected sensor range.
    Small random variation is added between readings so the resulting
    dataset behaves like a time series rather than repeated snapshots.
    """

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def generate_reading(
        self,
        machine_config: MachineConfig,
        health: MachineHealth,
    ) -> dict:
        """
        Generate one sensor reading for the current machine state.
        """

        if health.state == HealthState.NORMAL:
            reading = self._normal_reading(machine_config)

        elif health.state == HealthState.DEGRADING:
            reading = self._degrading_reading(machine_config)

        elif health.state == HealthState.AT_RISK:
            reading = self._at_risk_reading(machine_config)

        else:
            reading = self._normal_reading(machine_config)

        reading = self._apply_sensor_variation(reading)
        reading = self._apply_anomaly(reading, machine_config)
        reading = self._apply_missing_values(reading)

        return reading

    def generate_shift_readings(
        self,
        machine_config: MachineConfig,
        health: MachineHealth,
        start_time,
        duration_hours: int = 8,
    ) -> list[dict]:
        """
        Generate sensor readings throughout a production shift.

        Default:
            08:00 -> 16:00
            15-minute interval

        This produces 32 readings per machine per shift.
        """

        readings = []

        current_time = start_time
        end_time = start_time + self._minutes_to_delta(
            duration_hours * 60
        )

        while current_time < end_time:
            reading = self.generate_reading(
                machine_config,
                health,
            )

            reading["timestamp"] = current_time

            readings.append(reading)

            current_time += self._minutes_to_delta(
                SENSOR_INTERVAL_MINUTES
            )

        return readings

    def _normal_reading(
        self,
        config: MachineConfig,
    ) -> dict:
        return {
            "temperature": self._random_value(
                config.temperature_min,
                config.temperature_max,
            ),
            "vibration": self._random_value(
                config.vibration_min,
                config.vibration_max,
            ),
            "pressure": self._random_value(
                config.pressure_min,
                config.pressure_max,
            ),
            "power_consumption": self._random_value(
                config.power_min,
                config.power_max,
            ),
        }

    def _degrading_reading(
        self,
        config: MachineConfig,
    ) -> dict:
        return {
            "temperature": self._random_value(
                config.temperature_max,
                config.temperature_max * 1.08,
            ),
            "vibration": self._random_value(
                config.vibration_max,
                config.vibration_max * 1.20,
            ),
            "pressure": self._random_value(
                config.pressure_min * 0.95,
                config.pressure_max * 1.05,
            ),
            "power_consumption": self._random_value(
                config.power_max,
                config.power_max * 1.10,
            ),
        }

    def _at_risk_reading(
        self,
        config: MachineConfig,
    ) -> dict:
        return {
            "temperature": self._random_value(
                config.temperature_max * 1.05,
                config.temperature_max * 1.20,
            ),
            "vibration": self._random_value(
                config.vibration_max * 1.20,
                config.vibration_max * 1.60,
            ),
            "pressure": self._random_value(
                config.pressure_min * 0.80,
                config.pressure_max * 1.20,
            ),
            "power_consumption": self._random_value(
                config.power_max * 1.10,
                config.power_max * 1.30,
            ),
        }

    def _apply_sensor_variation(
        self,
        reading: dict,
    ) -> dict:
        """
        Add small natural variation between consecutive readings.
        """

        variation_ranges = {
            "temperature": 0.015,
            "vibration": 0.025,
            "pressure": 0.020,
            "power_consumption": 0.020,
        }

        varied_reading = {}

        for sensor_name, value in reading.items():
            variation = variation_ranges[sensor_name]

            multiplier = self.random.uniform(
                1.0 - variation,
                1.0 + variation,
            )

            varied_reading[sensor_name] = round(
                value * multiplier,
                3,
            )

        return varied_reading

    def _apply_anomaly(
        self,
        reading: dict,
        config: MachineConfig,
    ) -> dict:
        """
        Occasionally inject a sensor anomaly.

        Anomalies represent unusual sensor behavior that may later
        be detected by the anomaly-detection pipeline.
        """

        if self.random.random() >= SENSOR_ANOMALY_RATE:
            return reading

        anomaly_sensor = self.random.choice(
            [
                "temperature",
                "vibration",
                "pressure",
                "power_consumption",
            ]
        )

        if anomaly_sensor == "temperature":
            reading["temperature"] = round(
                reading["temperature"]
                * self.random.uniform(1.10, 1.25),
                3,
            )

        elif anomaly_sensor == "vibration":
            reading["vibration"] = round(
                reading["vibration"]
                * self.random.uniform(1.25, 1.60),
                3,
            )

        elif anomaly_sensor == "pressure":
            reading["pressure"] = round(
                reading["pressure"]
                * self.random.uniform(0.70, 1.30),
                3,
            )

        elif anomaly_sensor == "power_consumption":
            reading["power_consumption"] = round(
                reading["power_consumption"]
                * self.random.uniform(1.15, 1.35),
                3,
            )

        return reading

    def _apply_missing_values(
        self,
        reading: dict,
    ) -> dict:
        """
        Randomly simulate missing sensor values.
        """

        for sensor_name in reading:
            if self.random.random() < SENSOR_MISSING_RATE:
                reading[sensor_name] = None

        return reading

    @staticmethod
    def _random_value(
        minimum: float,
        maximum: float,
    ) -> float:
        return round(
            random.uniform(minimum, maximum),
            3,
        )

    @staticmethod
    def _minutes_to_delta(minutes: int):
        from datetime import timedelta

        return timedelta(minutes=minutes)

