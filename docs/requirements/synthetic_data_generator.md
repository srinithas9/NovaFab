# NovaFab Synthetic Data Generator Specification

## 1. Purpose

NovaFab requires realistic factory data for development, analytics, machine learning, testing, and demonstration.

Real industrial datasets rarely provide all the operational information required by NovaFab in one consistent schema. Therefore, NovaFab will use a controlled synthetic factory data generator for its core operational data.

The generator must produce data that behaves like a simplified real manufacturing environment rather than independent random values.

The generated data should contain meaningful relationships between:

* Factory
* Machines
* Machine health
* Sensor readings
* Production
* Quality
* Defects
* Maintenance
* Machine recovery

The objective is to create data from which genuine analytical and machine-learning patterns can be discovered.

---

# 2. What the Generator Must Simulate

The generator represents a simplified manufacturing plant operating over time.

The main causal chain is:

```text
Machine Health
      ↓
Sensor Behavior
      ↓
Production Performance
      ↓
Quality Performance
      ↓
Defects
      ↓
Maintenance
      ↓
Machine Recovery
```

This does not mean every event is deterministically caused by the previous event.

Instead, the generator uses probabilistic relationships so that:

* healthy machines generally perform better,
* degrading machines generally show abnormal sensor behavior,
* degraded machines have higher production and quality problems,
* maintenance is more likely when machine condition deteriorates,
* maintenance improves machine condition,
* random variation still exists.

This creates realistic noise while preserving useful operational relationships.

---

# 3. Generator Design Principles

## 3.1 Relationship over randomness

The generator must not independently generate every CSV file.

For example, this would be incorrect:

```text
Random sensors
Random production
Random quality
Random maintenance
```

Instead:

```text
Machine state
     ↓
Sensors
     ↓
Production
     ↓
Quality
     ↓
Defects
     ↓
Maintenance
```

The datasets should therefore be statistically related.

---

## 3.2 Reproducibility

The generator must use a fixed random seed.

Example:

```python
RANDOM_SEED = 42
```

Using the same configuration and seed should reproduce the same dataset.

This is important for:

* debugging,
* testing,
* model comparison,
* experiment reproducibility,
* demonstrations,
* interview explanations.

---

## 3.3 Configurability

Dataset size and simulation parameters must not be hard-coded throughout the generator.

Important configuration values should be centralized.

Examples:

```text
Number of factories
Number of machines
Simulation start date
Simulation end date
Sensor frequency
Production frequency
Maintenance probability
Failure probability
Random seed
```

This allows NovaFab to generate small datasets for development and larger datasets for testing.

---

## 3.4 Source-system simulation

The generator should behave as though the data came from multiple factory systems.

Conceptually:

```text
Factory Master System
        ↓
Machine Master System
        ↓
Machine Sensor System
        ↓
Production System
        ↓
Quality System
        ↓
Maintenance System
```

The output of these simulated systems becomes the raw ingestion layer.

---

# 4. Factory Configuration

The initial NovaFab environment contains one factory.

```text
Factory Code:
NF-PLANT-01

Name:
NovaFab Manufacturing Plant

Location:
Bengaluru, Karnataka

Industry:
Discrete Manufacturing
```

The generator should be designed so additional factories can be added later through configuration.

---

# 5. Machine Configuration

The initial factory contains nine machines.

| Machine Code | Machine Name            | Machine Type |
| ------------ | ----------------------- | ------------ |
| CNC-001      | CNC Machining Center A1 | CNC          |
| PRS-001      | Hydraulic Press A1      | Press        |
| ROB-001      | Assembly Robot A1       | Robot        |
| CNC-002      | CNC Machining Center B1 | CNC          |
| WLD-001      | Robotic Welding Cell B1 | Welding      |
| ROB-002      | Assembly Robot B1       | Robot        |
| CON-001      | Main Conveyor C1        | Conveyor     |
| PKG-001      | Automated Packaging C1  | Packaging    |
| LAB-001      | Labeling Machine C1     | Labeling     |

Machine configuration should eventually allow machine-specific operating parameters.

Examples:

```text
Normal temperature range
Normal vibration range
Normal pressure range
Normal power range
Production capacity
Maintenance interval
Risk sensitivity
```

This is important because a CNC machine should not behave exactly like a conveyor or packaging machine.

---

# 6. Simulation Time

The generator should simulate factory activity across a configurable time period.

Initial target:

```text
Start: 2026-01-01
End:   2026-09-30
```

The exact period should be configurable rather than hard-coded.

Sensor readings should occur at a higher frequency than production or maintenance events.

Conceptually:

```text
Sensor readings
    → frequent

Production runs
    → periodic

Quality inspections
    → associated with production batches

Maintenance
    → occasional

Factory-level events
    → event driven
```

---

# 7. Machine Health State Model

Each machine has a hidden operational health state.

The initial state is generally:

```text
NORMAL
```

The machine can transition through:

```text
NORMAL
   ↓
DEGRADING
   ↓
AT_RISK
   ↓
MAINTENANCE
   ↓
NORMAL
```

A machine does not need to follow this path every time.

For example:

```text
NORMAL → NORMAL
NORMAL → DEGRADING
DEGRADING → NORMAL
DEGRADING → AT_RISK
AT_RISK → MAINTENANCE
MAINTENANCE → NORMAL
```

The state transition process should be probabilistic and influenced by time, machine behavior, and previous condition.

---

# 8. Health State Definitions

## 8.1 NORMAL

The machine is operating within expected conditions.

Expected behavior:

* stable temperature,
* stable vibration,
* stable pressure,
* normal power consumption,
* high production efficiency,
* low rejection rate,
* low defect probability.

---

## 8.2 DEGRADING

The machine is beginning to deteriorate.

Expected behavior:

* gradually increasing temperature,
* gradually increasing vibration,
* small pressure variation,
* increasing power consumption,
* slightly reduced production efficiency,
* increasing rejection probability.

---

## 8.3 AT_RISK

The machine shows significant abnormal behavior.

Expected behavior:

* elevated temperature,
* elevated vibration,
* abnormal pressure,
* increased power consumption,
* reduced production efficiency,
* increased rejection rate,
* increased defect probability,
* higher maintenance probability.

---

## 8.4 MAINTENANCE

The machine is undergoing maintenance.

Expected behavior:

* production may stop,
* sensor readings may be unavailable or reduced,
* maintenance activity is recorded.

After maintenance, the machine returns toward a healthy state.

---

# 9. Machine Health Score

The generator should internally maintain a normalized machine health value.

Example:

```text
1.00 → excellent health
0.80 → healthy
0.60 → degrading
0.40 → at risk
0.20 → severe condition
```

The exact thresholds are configurable.

The health score is an internal simulation variable.

It does not necessarily need to be written directly to the raw sensor CSV.

This distinction is important because:

```text
Raw source data
≠
Derived analytics
```

The application can later calculate health scores from observable sensor and operational data.

---

# 10. Sensor Simulation

The generator creates:

```text
temperature
vibration
pressure
power_consumption
```

for each machine.

Sensor values should depend on:

```text
Machine type
+
Machine health
+
Normal operating baseline
+
Time variation
+
Random noise
```

Conceptually:

```text
Sensor Value
=
Baseline
+
Health Effect
+
Time Effect
+
Random Noise
```

---

# 11. Sensor Correlation

The generator should intentionally create realistic relationships.

For example:

```text
Machine degradation
       ↓
Temperature ↑
       ↓
Vibration ↑
       ↓
Power consumption ↑
```

Another example:

```text
Machine degradation
       ↓
Production efficiency ↓
       ↓
Rejected quantity ↑
       ↓
Defect probability ↑
```

These relationships allow later analytics and ML models to identify patterns.

---

# 12. Sensor Noise

Real sensors are not perfectly stable.

Therefore, readings should contain controlled random variation.

For example:

```text
Expected temperature = 70
Possible readings:

69.7
70.4
70.1
69.9
70.8
```

The noise should be small enough that the underlying signal remains meaningful.

The generator must avoid extreme random fluctuations that have no relationship to machine condition.

---

# 13. Machine-Specific Sensor Behavior

Different machine types should have different operating characteristics.

For example:

### CNC

Important signals:

* temperature,
* vibration,
* power consumption.

### Press

Important signals:

* pressure,
* vibration,
* power consumption.

### Robot

Important signals:

* vibration,
* temperature,
* power consumption.

### Conveyor

Important signals:

* vibration,
* temperature,
* power consumption.

### Packaging

Important signals:

* temperature,
* vibration,
* power consumption.

These differences make the dataset more realistic and prevent every machine from looking identical.

---

# 14. Production Simulation

Production runs are generated for active machines.

Each production run contains:

```text
machine_code
product_code
batch_number
start_time
end_time
target_quantity
produced_quantity
rejected_quantity
```

Production performance depends on machine condition.

---

# 15. Production Efficiency

Production efficiency can be represented conceptually as:

```text
production_efficiency
=
produced_quantity / target_quantity
```

Healthy machines should generally have higher efficiency.

As machine health deteriorates:

```text
Health ↓
   ↓
Production efficiency ↓
   ↓
Rejected quantity ↑
```

However, random variation should remain so that the relationship is not perfectly deterministic.

---

# 16. Product Configuration

The generator should use a controlled product catalogue.

Example:

```text
PRD-1001
PRD-1002
PRD-1003
PRD-1004
PRD-1005
```

Different machine types may be assigned different compatible products.

This allows future analytics such as:

* product-level defect rate,
* machine-product relationships,
* production volume by product,
* quality variation by product.

---

# 17. Batch Generation

Every production run receives a unique batch number.

Example:

```text
BATCH-2026-000001
BATCH-2026-000002
BATCH-2026-000003
```

The batch number becomes the business identifier linking production and quality data.

---

# 18. Quality Simulation

Each production batch may receive a quality inspection.

Possible results:

```text
PASS
FAIL
REVIEW
```

The probability of each result depends on:

```text
Machine health
+
Production performance
+
Product characteristics
+
Random variation
```

Healthy machines should generally produce more PASS results.

Degraded machines should have higher REVIEW and FAIL probabilities.

---

# 19. Defect Simulation

Defects are generated for batches with quality issues.

Possible defect types:

```text
Surface Defect
Dimensional Error
Alignment Error
Weld Defect
Labeling Error
Packaging Defect
Assembly Error
```

Possible severity:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The probability and severity of defects should increase with machine degradation.

---

# 20. Maintenance Simulation

Maintenance records represent operational interventions.

Maintenance types:

```text
PREVENTIVE
CORRECTIVE
INSPECTION
```

Maintenance status:

```text
SCHEDULED
IN_PROGRESS
COMPLETED
```

Corrective maintenance should be more likely when machine health deteriorates.

---

# 21. Preventive Maintenance

Preventive maintenance should be generated according to configured maintenance intervals.

Example:

```text
Every N operating days
```

This prevents the dataset from containing only failure-driven maintenance.

---

# 22. Corrective Maintenance

Corrective maintenance is triggered probabilistically when machine condition becomes sufficiently poor.

Conceptually:

```text
Health decreases
      ↓
Risk increases
      ↓
Corrective maintenance probability increases
      ↓
Maintenance event
      ↓
Health recovery
```

---

# 23. Maintenance Recovery

Maintenance should have an effect on future machine behavior.

Example:

```text
Before maintenance:

Health = 0.35
Temperature = high
Vibration = high
Production efficiency = low

After maintenance:

Health = 0.90
Temperature = normal
Vibration = normal
Production efficiency = improved
```

The recovery should not always be perfect.

This allows future ML models to learn realistic post-maintenance behavior.

---

# 24. Quality-Maintenance Relationship

Maintenance should indirectly influence quality.

Example:

```text
Poor machine condition
        ↓
Higher defect probability
        ↓
Quality problems
        ↓
Maintenance
        ↓
Improved machine condition
        ↓
Lower defect probability
```

This gives NovaFab a meaningful operational story instead of isolated datasets.

---

# 25. Data Generation Order

The generator should follow a controlled order.

```text
1. Factory master data
        ↓
2. Machine master data
        ↓
3. Product configuration
        ↓
4. Machine health simulation
        ↓
5. Sensor readings
        ↓
6. Production runs
        ↓
7. Quality inspections
        ↓
8. Defects
        ↓
9. Maintenance records
        ↓
10. Validation
        ↓
11. CSV output
```

This order ensures that downstream records can reference upstream business identifiers.

---

# 26. Raw Output Files

The generator must create:

```text
data/raw/
├── factories.csv
├── machines.csv
├── sensor_readings.csv
├── production_runs.csv
├── maintenance_records.csv
├── quality_inspections.csv
└── defects.csv
```

The generator should not directly insert data into PostgreSQL.

---

# 27. Generator vs Database Responsibility

The generator is responsible for:

* simulating factory behavior,
* creating source data,
* maintaining business-key relationships,
* generating realistic variation,
* producing reproducible CSV files.

The ingestion pipeline is responsible for:

* schema validation,
* data-type validation,
* missing-value validation,
* business-rule validation,
* business-key resolution,
* transformation,
* PostgreSQL loading.

Django is responsible for:

* application models,
* database constraints,
* APIs,
* business application logic,
* authentication and authorization.

---

# 28. Validation Requirements

The generated data must pass validation before being considered usable.

Validation should check:

### Factory

* factory codes are unique.

### Machines

* machine codes are unique.
* every machine references a valid factory.

### Sensors

* every machine code exists.
* timestamps are valid.
* numeric values are within reasonable ranges.

### Production

* batch numbers are unique.
* machine codes exist.
* end time is after start time.
* produced quantity is non-negative.
* rejected quantity is non-negative.
* rejected quantity does not exceed produced quantity.

### Quality

* referenced machine exists.
* referenced batch exists.
* result is valid.
* defect count is non-negative.

### Defects

* referenced batch exists.
* severity is valid.

### Maintenance

* machine exists.
* maintenance type is valid.
* completed date cannot precede scheduled date when both exist.

---

# 29. Data Quality Requirements

The generated dataset should contain realistic variation.

It should NOT contain:

```text
100% perfect machines
100% perfect production
zero defects
zero missing values
identical sensor readings
identical machine behavior
perfect linear relationships
```

Controlled imperfections should exist because real operational data contains noise and exceptions.

---

# 30. Missing Data

Some missing values may be intentionally introduced.

Examples:

* temporary sensor outage,
* incomplete technician notes,
* missing completed date for scheduled maintenance,
* occasional unavailable sensor reading.

Missingness should be controlled and documented.

It should not be generated randomly without a reason.

---

# 31. Failure Injection

The generator should support configurable abnormal scenarios.

Examples:

```text
Sensor spike
Sensor drift
Machine degradation
Unexpected production slowdown
Quality deterioration
Maintenance delay
Temporary sensor outage
```

These scenarios will later help test:

* anomaly detection,
* alert generation,
* predictive maintenance,
* data-quality monitoring,
* dashboard behavior.

---

# 32. Expected Data Relationships

The final dataset should approximately exhibit relationships such as:

```text
Machine health ↓
    ↓
Temperature ↑
Vibration ↑
Power consumption ↑
    ↓
Production efficiency ↓
    ↓
Rejected quantity ↑
    ↓
Defect probability ↑
    ↓
Maintenance probability ↑
```

After maintenance:

```text
Maintenance
    ↓
Machine health ↑
    ↓
Sensor values move toward baseline
    ↓
Production efficiency improves
    ↓
Quality improves
```

These are expected simulation relationships, not guaranteed relationships for every individual record.

---

# 33. Target Dataset Size

Initial target:

| Dataset             | Approximate Target |
| ------------------- | -----------------: |
| Factories           |                  1 |
| Machines            |                  9 |
| Sensor readings     |           100,000+ |
| Production runs     |             10,000 |
| Maintenance records |               ~500 |
| Quality inspections |            ~10,000 |
| Defects             |   Several thousand |

These values are configurable.

The generator should support smaller datasets for development and larger datasets for performance testing.

---

# 34. Reproducibility Metadata

The generator should record its configuration.

Example metadata:

```text
Generator version
Random seed
Simulation start date
Simulation end date
Number of machines
Sensor frequency
Generator timestamp
```

This allows a generated dataset to be traced back to the configuration that produced it.

---

# 35. Recommended Generator Structure

The generator should eventually be implemented as modular Python code.

Proposed structure:

```text
scripts/
└── generate_data/
    ├── __init__.py
    ├── config.py
    ├── random_utils.py
    ├── factory_generator.py
    ├── machine_generator.py
    ├── health_simulator.py
    ├── sensor_generator.py
    ├── product_generator.py
    ├── production_generator.py
    ├── quality_generator.py
    ├── defect_generator.py
    ├── maintenance_generator.py
    ├── validators.py
    ├── writer.py
    └── main.py
```

The exact structure may be adjusted during implementation.

---

# 36. Why Modular Generation

A single large Python script would be difficult to:

* understand,
* test,
* debug,
* modify,
* reuse.

Separating the generator into modules allows each responsibility to be tested independently.

For example:

```text
health_simulator.py
```

should focus on machine health behavior.

```text
sensor_generator.py
```

should focus on sensor readings.

```text
validators.py
```

should focus on data quality.

---

# 37. Generator Execution

The eventual generator should be executable through one clear command.

Example:

```powershell
python scripts/generate_data/main.py
```

Optional configuration may later be supported.

Example:

```powershell
python scripts/generate_data/main.py --seed 42
```

The command should:

1. Load configuration.
2. Generate factory data.
3. Generate machine data.
4. Simulate machine health.
5. Generate sensor data.
6. Generate production data.
7. Generate quality data.
8. Generate defects.
9. Generate maintenance records.
10. Validate the generated datasets.
11. Write valid CSV files.
12. Report generation statistics.

---

# 38. Example Final Console Output

The generator should eventually provide a summary similar to:

```text
NovaFab Synthetic Data Generator
---------------------------------

Seed: 42
Simulation period: 2026-01-01 → 2026-09-30

Factories generated:          1
Machines generated:           9
Sensor readings generated:    108,432
Production runs generated:    10,214
Quality inspections:          9,876
Defects generated:            3,241
Maintenance records:          487

Validation:
Factories:       PASS
Machines:        PASS
Sensors:         PASS
Production:      PASS
Quality:         PASS
Defects:         PASS
Maintenance:     PASS

Output:
data/raw/

Generation completed successfully.
```

The exact numbers will depend on the configuration and random seed.

---

# 39. Future Extensions

The generator should be designed so the following can be added later without redesigning the entire system:

* multiple factories,
* additional machine types,
* additional sensors,
* shift information,
* operators,
* energy consumption,
* downtime events,
* spare parts,
* maintenance costs,
* production schedules,
* suppliers,
* environmental conditions,
* machine failure events,
* anomaly scenarios.

These are future extensions and should not be implemented unless required by the project.

---

# 40. Important Architectural Rule

NovaFab should not create technology for the sake of complexity.

The synthetic generator exists because NovaFab needs controlled operational data that supports:

1. Data Engineering
2. Data Analytics
3. Machine Learning
4. Predictive Maintenance
5. Quality Intelligence
6. Computer Vision integration
7. RAG and operational knowledge
8. Decision-support workflows

Every generated field should therefore have a reason to exist.

If a field does not support a business question, analytical requirement, ML feature, relationship, or application workflow, it should not be added merely to make the dataset look larger.

---

# 41. Final Simulation Model

The overall simulation can be summarized as:

```text
                    FACTORY
                       │
                       ▼
                   MACHINES
                       │
                       ▼
                MACHINE HEALTH
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       SENSORS      PRODUCTION   MAINTENANCE
          │            │
          │            ▼
          │          QUALITY
          │            │
          │            ▼
          │          DEFECTS
          │            │
          └────────────┴────────────┐
                                    ▼
                              OPERATIONAL
                               BEHAVIOR
                                    │
                                    ▼
                            NOVAFAB ANALYTICS
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
                 Analytics         ML             AI/RAG
```

The generator therefore acts as the controlled operational foundation for the rest of NovaFab.
