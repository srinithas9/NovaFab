# Raw Data Schemas

## 1. factories.csv

| Column | Description |
|---|---|
| factory_code | Unique business identifier for the factory |
| name | Factory name |
| location | Factory location |
| industry | Factory industry |

---

## 2. machines.csv

| Column | Description |
|---|---|
| machine_code | Unique business identifier for the machine |
| factory_code | Factory to which the machine belongs |
| name | Machine name |
| machine_type | Type/category of machine |
| installation_date | Date the machine was installed |
| is_active | Whether the machine is currently active |

---

## 3. sensor_readings.csv

| Column | Description |
|---|---|
| machine_code | Machine generating the reading |
| timestamp | Time of sensor measurement |
| temperature | Machine temperature |
| vibration | Machine vibration measurement |
| pressure | Machine pressure measurement |
| power_consumption | Machine power consumption |

---

## 4. production_runs.csv

| Column | Description |
|---|---|
| machine_code | Machine used for production |
| product_code | Product being manufactured |
| batch_number | Unique production batch identifier |
| start_time | Production start time |
| end_time | Production end time |
| target_quantity | Planned production quantity |
| produced_quantity | Actual quantity produced |
| rejected_quantity | Quantity rejected during production |

---

## 5. maintenance_records.csv

| Column | Description |
|---|---|
| machine_code | Machine receiving maintenance |
| maintenance_type | Type of maintenance |
| status | Maintenance status |
| scheduled_date | Scheduled maintenance date |
| completed_date | Actual completion date |
| description | Description of maintenance activity |
| technician_notes | Technician observations |

---

## 6. quality_inspections.csv

| Column | Description |
|---|---|
| machine_code | Machine that produced the inspected batch |
| batch_number | Production batch being inspected |
| inspection_time | Time of inspection |
| result | PASS, FAIL, or REVIEW |
| defect_count | Number of defects identified |
| inspector_notes | Inspector observations |

---

## 7. defects.csv

| Column | Description |
|---|---|
| batch_number | Production batch associated with the defect |
| defect_type | Type of defect |
| severity | Defect severity |
| description | Description of the defect |

---

# 8. Raw Data Relationships

```text
factories.csv
      │
      │ factory_code
      ▼
machines.csv
      │
      │ machine_code
      ├───────────────► sensor_readings.csv
      │
      ├───────────────► production_runs.csv
      │                       │
      │                       │ batch_number
      │                       ▼
      │               quality_inspections.csv
      │                       │
      │                       │ batch_number
      │                       ▼
      │                  defects.csv
      │
      └───────────────► maintenance_records.csv
      