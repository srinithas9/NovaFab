# NovaFab Maintenance Lifecycle

## 1. Purpose

The maintenance lifecycle defines how NovaFab simulates preventive,
corrective, and inspection maintenance events without creating duplicate
maintenance records for the same maintenance episode.

---

## 2. Maintenance States

A maintenance event can have three operational statuses:

- SCHEDULED
- IN_PROGRESS
- COMPLETED

These statuses represent the progress of a maintenance event.

---

## 3. Maintenance Lifecycle

The normal lifecycle is:

SCHEDULED
    ↓
IN_PROGRESS
    ↓
COMPLETED

A maintenance event should represent one maintenance episode.

The simulator must not create a second maintenance event while the
current maintenance event is still active.

---

## 4. Preventive Maintenance

Preventive maintenance is date-driven.

A machine receives a preventive maintenance event when:

current_date >= next_preventive_maintenance_date

Once the event is created:

- The machine is considered to have an active maintenance event.
- The simulator must not create another preventive maintenance event
  while the current event is active.
- When the event is completed, a new preventive maintenance date is
  scheduled.

Example:

2026-02-20
    ↓
Preventive maintenance due
    ↓
Maintenance event created
    ↓
IN_PROGRESS
    ↓
No duplicate maintenance event
    ↓
COMPLETED
    ↓
Next preventive date calculated

---

## 5. Corrective Maintenance

Corrective maintenance is condition-driven.

It may occur when a machine enters a degraded or at-risk condition.

The probability of corrective maintenance increases as machine health
worsens.

A corrective maintenance event follows the same lifecycle:

SCHEDULED
    ↓
IN_PROGRESS
    ↓
COMPLETED

An active corrective maintenance event prevents another maintenance
event from being created for the same machine until the current event
is completed.

---

## 6. Maintenance and Machine Health

Maintenance affects machine health only when maintenance is completed.

If maintenance is:

SCHEDULED
or
IN_PROGRESS

the machine health continues according to the normal simulation rules.

If maintenance is:

COMPLETED

the health simulator applies recovery.

Example:

AT_RISK
0.59 health
    ↓
Maintenance IN_PROGRESS
    ↓
Health remains degraded
    ↓
Maintenance COMPLETED
    ↓
Health recovery
    ↓
DEGRADING / NORMAL

---

## 7. Active Maintenance Rule

Each machine should have at most one active maintenance event.

Active maintenance means:

- SCHEDULED
- IN_PROGRESS

If an active maintenance event exists:

- Do not create another maintenance event.
- Continue processing the existing event.

Only after the event becomes COMPLETED can a new maintenance event
be scheduled.

---

## 8. Preventive Maintenance Date

After completed preventive maintenance:

next_preventive_maintenance_date

must be recalculated from the completion date.

Example:

Maintenance completed:
2026-02-20

Preventive interval:
30–60 days

Possible next date:
2026-04-14

The next date must be later than the completed maintenance date.

---

## 9. Why This Design Is Required

Without an active-maintenance state, a simulation running every 15 minutes
could repeatedly generate maintenance records after a maintenance date
has passed.

For example:

10:00 → maintenance created
10:15 → another maintenance created
10:30 → another maintenance created
10:45 → another maintenance created

This would produce unrealistic duplicate records.

The active-maintenance rule prevents this problem.

---

## 10. Simulation Principle

The simulator should model a maintenance event as a stateful process,
not as an independent random event at every simulation step.

Therefore:

Machine
    ↓
Maintenance decision
    ↓
Maintenance lifecycle
    ↓
Health response
    ↓
Sensor / production / quality outcomes