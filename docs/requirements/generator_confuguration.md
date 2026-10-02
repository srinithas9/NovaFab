# NovaFab Generator Configuration

## 1. Purpose

This document defines the configuration used by the NovaFab synthetic factory data generator.

The configuration controls:

* simulation period,
* factory and machine counts,
* sensor generation frequency,
* machine operating ranges,
* production capacity,
* health degradation,
* maintenance behavior,
* quality behavior,
* random variation.

The values are centralized so that the generator logic does not contain unexplained hard-coded numbers.

---

# 2. Global Configuration

| Parameter              | Initial Value | Purpose                      |
| ---------------------- | ------------: | ---------------------------- |
| Random seed            |            42 | Reproducible data generation |
| Simulation start       |    2026-01-01 | Start of simulation          |
| Simulation end         |    2026-09-30 | End of simulation            |
| Factory count          |             1 | Initial factory count        |
| Machine count          |             9 | Initial machine count        |
| Sensor frequency       |    15 minutes | Sensor sampling interval     |
| Minimum production run |    30 minutes | Minimum run duration         |
| Maximum production run |       8 hours | Maximum run duration         |

The configuration should be adjustable later without modifying the core generation algorithms.

---

# 3. Factory Configuration

Initial factory:

| Field        | Value                       |
| ------------ | --------------------------- |
| Factory Code | NF-PLANT-01                 |
| Name         | NovaFab Manufacturing Plant |
| Location     | Bengaluru, Karnataka        |
| Industry     | Discrete Manufacturing      |

---

# 4. Machine Configuration

Each machine has machine-specific operating characteristics.

| Machine | Type      | Temperature °C | Vibration | Pressure | Power kW |
| ------- | --------- | -------------: | --------: | -------: | -------: |
| CNC-001 | CNC       |          60–75 |   1.0–2.5 |   80–110 |    18–30 |
| PRS-001 | Press     |          50–70 |   1.5–3.0 |  120–180 |    20–35 |
| ROB-001 | Robot     |          35–55 |   0.5–1.5 |   70–100 |     8–15 |
| CNC-002 | CNC       |          60–75 |   1.0–2.5 |   80–110 |    18–30 |
| WLD-001 | Welding   |          45–65 |   1.0–2.5 |   90–130 |    15–28 |
| ROB-002 | Robot     |          35–55 |   0.5–1.5 |   70–100 |     8–15 |
| CON-001 | Conveyor  |          30–50 |   0.5–1.8 |    40–70 |     5–12 |
| PKG-001 | Packaging |          35–55 |   0.5–1.5 |    50–80 |     6–14 |
| LAB-001 | Labeling  |          30–50 |   0.3–1.2 |    40–70 |     4–10 |

These ranges represent normal operating ranges.

They are not failure thresholds.

---

# 5. Sensor Generation Rules

Sensor values should be generated around a machine-specific baseline.

The conceptual model is:

```text
Sensor Value
=
Normal Baseline
+
Health Effect
+
Time Variation
+
Random Noise
```

The generator should not simply select a random number between the minimum and maximum value.

For example, if a CNC machine normally operates around 68°C, most healthy readings should remain close to that value.

---

# 6. Health Impact on Sensors

As machine health deteriorates, sensor values move away from their normal operating range.

| Health State | Sensor Behavior                     |
| ------------ | ----------------------------------- |
| NORMAL       | Near normal baseline                |
| DEGRADING    | Small drift from baseline           |
| AT_RISK      | Significant deviation               |
| MAINTENANCE  | Sensor readings reduced/unavailable |
| RECOVERED    | Gradual return toward baseline      |

General behavior:

```text
Health ↓
   │
   ├── Temperature ↑
   ├── Vibration ↑
   ├── Power consumption ↑
   └── Pressure becomes less stable
```

The exact effect should vary by machine type.

---

# 7. Health Score Configuration

Internal machine health is represented on a 0–1 scale.

| Health Score | State                            |
| -----------: | -------------------------------- |
|    0.80–1.00 | NORMAL                           |
|    0.60–0.79 | DEGRADING                        |
|    0.30–0.59 | AT_RISK                          |
|    0.00–0.29 | CRITICAL / Maintenance Candidate |

The health score is an internal simulation variable.

It should not automatically be stored as a raw sensor field.

---

# 8. Health Degradation

Healthy machines should gradually degrade rather than suddenly failing in most cases.

Conceptually:

```text
Normal
  ↓
Small degradation
  ↓
Continued degradation
  ↓
At Risk
  ↓
Maintenance
  ↓
Recovery
```

The degradation rate should include random variation.

This prevents every machine from following the exact same lifecycle.

---

# 9. Production Configuration

Each machine has an approximate production capacity.

Initial configuration:

| Machine Type | Approx. Target Units / Run |
| ------------ | -------------------------: |
| CNC          |                     80–160 |
| Press        |                    100–220 |
| Robot        |                    120–250 |
| Welding      |                     80–180 |
| Conveyor     |                    150–300 |
| Packaging    |                    120–250 |
| Labeling     |                    150–300 |

Actual production should vary based on:

* machine condition,
* product,
* run duration,
* normal operational variation.

---

# 10. Production Efficiency

Healthy machines should normally operate at approximately:

```text
90%–100%
```

Degrading machines:

```text
80%–95%
```

At-risk machines:

```text
60%–85%
```

These are simulation ranges, not fixed outputs.

Random variation should be applied within and around these ranges.

---

# 11. Rejection Configuration

Healthy machines should have relatively low rejection rates.

Example target behavior:

| Machine State | Typical Rejection Rate |
| ------------- | ---------------------: |
| NORMAL        |                   1–3% |
| DEGRADING     |                   2–6% |
| AT_RISK       |                  5–15% |

These values should be probabilistic.

Individual production runs may fall outside the typical range.

---

# 12. Quality Configuration

Possible quality outcomes:

```text
PASS
REVIEW
FAIL
```

Approximate behavior:

### NORMAL

```text
PASS → high probability
REVIEW → low probability
FAIL → very low probability
```

### DEGRADING

```text
PASS → still common
REVIEW → increased
FAIL → increased
```

### AT_RISK

```text
PASS → reduced
REVIEW → increased
FAIL → significantly increased
```

Quality should depend on machine condition but should not be perfectly determined by it.

---

# 13. Defect Configuration

Initial defect categories:

```text
Surface Defect
Dimensional Error
Alignment Error
Weld Defect
Labeling Error
Packaging Defect
Assembly Error
```

Severity:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Expected relationship:

```text
Machine health ↓
       ↓
Defect probability ↑
       ↓
Defect severity probability ↑
```

---

# 14. Maintenance Configuration

Maintenance types:

```text
PREVENTIVE
CORRECTIVE
INSPECTION
```

Initial approximate distribution:

| Maintenance Type | Approximate Share |
| ---------------- | ----------------: |
| Preventive       |               55% |
| Corrective       |               30% |
| Inspection       |               15% |

These values are starting assumptions and can be adjusted after examining generated data.

---

# 15. Preventive Maintenance

Preventive maintenance should occur at configured operating intervals.

Initial target:

```text
Approximately every 30–60 operating days
```

The actual interval should vary.

This prevents all machines from receiving maintenance on exactly the same schedule.

---

# 16. Corrective Maintenance

Corrective maintenance becomes increasingly likely when machine health deteriorates.

Conceptually:

```text
Health > 0.70
    ↓
Low corrective-maintenance probability

Health 0.40–0.70
    ↓
Moderate probability

Health < 0.40
    ↓
High probability
```

Corrective maintenance should not be guaranteed at a particular health score.

---

# 17. Maintenance Recovery

After completed maintenance:

```text
Machine health
    ↓
moves toward healthy range
```

Initial recovery target:

```text
0.85–0.98
```

Recovery should contain some variation.

A machine should not always return to exactly `1.00`.

---

# 18. Sensor Missingness

The generator may introduce controlled missing values.

Initial target:

```text
Sensor missingness: approximately 0.5–2%
```

Possible reasons:

* sensor communication interruption,
* temporary sensor maintenance,
* data collection failure.

Missing values should be introduced intentionally and documented.

---

# 19. Sensor Anomalies

The generator should support controlled abnormal events.

Initial target:

```text
Anomaly rate: approximately 0.1–0.5%
```

Possible anomalies:

* temperature spike,
* vibration spike,
* pressure drop,
* power spike.

Anomalies should be rare enough to remain meaningful.

---

# 20. Time Variation

Factory behavior should not be identical at every hour.

The generator may introduce:

* shift effects,
* small daily variation,
* gradual machine drift,
* production variation.

For example:

```text
Morning shift
→ normal production

Peak operating period
→ slightly higher utilization

Low-utilization period
→ lower production activity
```

Time effects should remain subtle compared with machine-health effects.

---

# 21. Machine-Specific Behavior

Machine types should not use identical formulas.

For example:

```text
CNC
→ vibration and temperature are important

Press
→ pressure and vibration are important

Robot
→ vibration and power are important

Welding
→ temperature and power are important

Conveyor
→ vibration and power are important

Packaging
→ vibration and temperature are important

Labeling
→ vibration and power are important
```

This allows NovaFab to later perform machine-specific diagnostics.

---

# 22. Configuration Philosophy

The configuration values are not claimed to represent measurements from a real NovaFab factory.

They are simulation assumptions designed to create a plausible and internally consistent manufacturing environment.

If real factory data becomes available, these values should be replaced or calibrated using observed distributions.

---

# 23. Calibration Process

After the first dataset is generated, the configuration must be reviewed using:

* descriptive statistics,
* distributions,
* missing-value analysis,
* correlation analysis,
* machine-level comparisons,
* time-series plots,
* production-quality relationships.

The configuration should be adjusted if the generated data is:

* too clean,
* too noisy,
* unrealistic,
* overly correlated,
* insufficiently variable,
* unsuitable for ML.

---

# 24. Configuration Priority

When implementing the generator, the following priority should be maintained:

```text
1. Realistic relationships
2. Reproducibility
3. Data quality
4. Configurability
5. Dataset size
```

Large data volume is less important than meaningful data.

---

# 25. Final Configuration Model

The generator configuration can be viewed as:

```text
                 GLOBAL CONFIG
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Factory        Machine        Simulation
     Config         Config          Config
        │              │              │
        └──────────────┼──────────────┘
                       ▼
                 HEALTH MODEL
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
           Sensors  Production Quality
                         │        │
                         └───┬────┘
                             ▼
                          Defects
                             │
                             ▼
                        Maintenance
                             │
                             ▼
                          Recovery
```

This configuration becomes the foundation for the Python generator implementation.
