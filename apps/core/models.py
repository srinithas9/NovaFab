from django.db import models


class Factory(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Machine(models.Model):
    factory = models.ForeignKey(
        Factory,
        on_delete=models.CASCADE,
        related_name="machines",
    )
    machine_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    machine_type = models.CharField(max_length=100)
    installation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["machine_code"]

    def __str__(self):
        return f"{self.machine_code} - {self.name}"


class SensorReading(models.Model):
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="sensor_readings",
    )
    timestamp = models.DateTimeField()

    temperature = models.FloatField(null=True, blank=True)
    vibration = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    power_consumption = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["machine", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.machine.machine_code} - {self.timestamp}"


class MaintenanceRecord(models.Model):
    class MaintenanceType(models.TextChoices):
        PREVENTIVE = "PREVENTIVE", "Preventive"
        CORRECTIVE = "CORRECTIVE", "Corrective"
        INSPECTION = "INSPECTION", "Inspection"

    class MaintenanceStatus(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="maintenance_records",
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=MaintenanceType.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.COMPLETED,
    )
    scheduled_date = models.DateField()
    completed_date = models.DateField(null=True, blank=True)
    description = models.TextField()
    technician_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_date"]

    def __str__(self):
        return f"{self.machine.machine_code} - {self.maintenance_type}"


class ProductionRun(models.Model):
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="production_runs",
    )
    product_code = models.CharField(max_length=50)
    batch_number = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    target_quantity = models.PositiveIntegerField()
    produced_quantity = models.PositiveIntegerField(default=0)
    rejected_quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["machine", "start_time"]),
            models.Index(fields=["product_code", "batch_number"]),
        ]

    def __str__(self):
        return f"{self.product_code} - {self.batch_number}"


class QualityInspection(models.Model):
    class InspectionResult(models.TextChoices):
        PASS = "PASS", "Pass"
        FAIL = "FAIL", "Fail"
        REVIEW = "REVIEW", "Review"

    production_run = models.ForeignKey(
        ProductionRun,
        on_delete=models.CASCADE,
        related_name="quality_inspections",
    )
    inspection_time = models.DateTimeField()
    result = models.CharField(
        max_length=10,
        choices=InspectionResult.choices,
    )
    defect_count = models.PositiveIntegerField(default=0)
    inspector_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-inspection_time"]

    def __str__(self):
        return (
            f"{self.production_run.batch_number} - "
            f"{self.result}"
        )


class Defect(models.Model):
    class Severity(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    inspection = models.ForeignKey(
        QualityInspection,
        on_delete=models.CASCADE,
        related_name="defects",
    )
    defect_type = models.CharField(max_length=100)
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.defect_type} - {self.severity}"


class Alert(models.Model):
    class AlertType(models.TextChoices):
        MACHINE = "MACHINE", "Machine"
        QUALITY = "QUALITY", "Quality"
        PRODUCTION = "PRODUCTION", "Production"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    class Severity(models.TextChoices):
        INFO = "INFO", "Info"
        WARNING = "WARNING", "Warning"
        CRITICAL = "CRITICAL", "Critical"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        RESOLVED = "RESOLVED", "Resolved"

    factory = models.ForeignKey(
        Factory,
        on_delete=models.CASCADE,
        related_name="alerts",
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.CASCADE,
        related_name="alerts",
        null=True,
        blank=True,
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    detected_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["status", "severity"]),
            models.Index(fields=["machine", "detected_at"]),
        ]

    def __str__(self):
        return f"{self.severity} - {self.title}"