from dataclasses import dataclass
from datetime import date


# ============================================================
# Global Simulation Configuration
# ============================================================

RANDOM_SEED = 42

SIMULATION_START = date(2026, 1, 1)
SIMULATION_END = date(2026, 9, 30)

SENSOR_INTERVAL_MINUTES = 15


# ============================================================
# Factory Configuration
# ============================================================

FACTORY_CONFIG = {
    "factory_code": "NF-PLANT-01",
    "name": "NovaFab Manufacturing Plant",
    "location": "Bengaluru, Karnataka",
    "industry": "Discrete Manufacturing",
}


# ============================================================
# Machine Configuration
# ============================================================

@dataclass(frozen=True)
class MachineConfig:
    machine_code: str
    name: str
    machine_type: str

    # Normal operating ranges
    temperature_min: float
    temperature_max: float

    vibration_min: float
    vibration_max: float

    pressure_min: float
    pressure_max: float

    power_min: float
    power_max: float

    # Production capacity
    production_min: int
    production_max: int


MACHINE_CONFIGS = [
    MachineConfig(
        machine_code="CNC-001",
        name="CNC Machining Center A1",
        machine_type="CNC",
        temperature_min=60,
        temperature_max=75,
        vibration_min=1.0,
        vibration_max=2.5,
        pressure_min=80,
        pressure_max=110,
        power_min=18,
        power_max=30,
        production_min=80,
        production_max=160,
    ),
    MachineConfig(
        machine_code="PRS-001",
        name="Hydraulic Press A1",
        machine_type="Press",
        temperature_min=50,
        temperature_max=70,
        vibration_min=1.5,
        vibration_max=3.0,
        pressure_min=120,
        pressure_max=180,
        power_min=20,
        power_max=35,
        production_min=100,
        production_max=220,
    ),
    MachineConfig(
        machine_code="ROB-001",
        name="Assembly Robot A1",
        machine_type="Robot",
        temperature_min=35,
        temperature_max=55,
        vibration_min=0.5,
        vibration_max=1.5,
        pressure_min=70,
        pressure_max=100,
        power_min=8,
        power_max=15,
        production_min=120,
        production_max=250,
    ),
    MachineConfig(
        machine_code="CNC-002",
        name="CNC Machining Center B1",
        machine_type="CNC",
        temperature_min=60,
        temperature_max=75,
        vibration_min=1.0,
        vibration_max=2.5,
        pressure_min=80,
        pressure_max=110,
        power_min=18,
        power_max=30,
        production_min=80,
        production_max=160,
    ),
    MachineConfig(
        machine_code="WLD-001",
        name="Robotic Welding Cell B1",
        machine_type="Welding",
        temperature_min=45,
        temperature_max=65,
        vibration_min=1.0,
        vibration_max=2.5,
        pressure_min=90,
        pressure_max=130,
        power_min=15,
        power_max=28,
        production_min=80,
        production_max=180,
    ),
    MachineConfig(
        machine_code="ROB-002",
        name="Assembly Robot B1",
        machine_type="Robot",
        temperature_min=35,
        temperature_max=55,
        vibration_min=0.5,
        vibration_max=1.5,
        pressure_min=70,
        pressure_max=100,
        power_min=8,
        power_max=15,
        production_min=120,
        production_max=250,
    ),
    MachineConfig(
        machine_code="CON-001",
        name="Main Conveyor C1",
        machine_type="Conveyor",
        temperature_min=30,
        temperature_max=50,
        vibration_min=0.5,
        vibration_max=1.8,
        pressure_min=40,
        pressure_max=70,
        power_min=5,
        power_max=12,
        production_min=150,
        production_max=300,
    ),
    MachineConfig(
        machine_code="PKG-001",
        name="Automated Packaging C1",
        machine_type="Packaging",
        temperature_min=35,
        temperature_max=55,
        vibration_min=0.5,
        vibration_max=1.5,
        pressure_min=50,
        pressure_max=80,
        power_min=6,
        power_max=14,
        production_min=120,
        production_max=250,
    ),
    MachineConfig(
        machine_code="LAB-001",
        name="Labeling Machine C1",
        machine_type="Labeling",
        temperature_min=30,
        temperature_max=50,
        vibration_min=0.3,
        vibration_max=1.2,
        pressure_min=40,
        pressure_max=70,
        power_min=4,
        power_max=10,
        production_min=150,
        production_max=300,
    ),
]


# ============================================================
# Health Configuration
# ============================================================

HEALTH_THRESHOLDS = {
    "normal": 0.80,
    "degrading": 0.60,
    "at_risk": 0.30,
}


# ============================================================
# Production Configuration
# ============================================================

PRODUCTION_EFFICIENCY = {
    "normal": (0.90, 1.00),
    "degrading": (0.80, 0.95),
    "at_risk": (0.60, 0.85),
}


REJECTION_RATES = {
    "normal": (0.01, 0.03),
    "degrading": (0.02, 0.06),
    "at_risk": (0.05, 0.15),
}


# ============================================================
# Quality Configuration
# ============================================================

QUALITY_RESULTS = (
    "PASS",
    "REVIEW",
    "FAIL",
)


DEFECT_TYPES = (
    "Surface Defect",
    "Dimensional Error",
    "Alignment Error",
    "Weld Defect",
    "Labeling Error",
    "Packaging Defect",
    "Assembly Error",
)


DEFECT_SEVERITIES = (
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)


# ============================================================
# Maintenance Configuration
# ============================================================

MAINTENANCE_TYPES = (
    "PREVENTIVE",
    "CORRECTIVE",
    "INSPECTION",
)


MAINTENANCE_STATUSES = (
    "SCHEDULED",
    "IN_PROGRESS",
    "COMPLETED",
)


MAINTENANCE_TYPE_WEIGHTS = {
    "PREVENTIVE": 0.55,
    "CORRECTIVE": 0.30,
    "INSPECTION": 0.15,
}


PREVENTIVE_MAINTENANCE_DAYS = (
    30,
    60,
)


# ============================================================
# Data Quality Configuration
# ============================================================

SENSOR_MISSING_RATE = 0.01

SENSOR_ANOMALY_RATE = 0.003