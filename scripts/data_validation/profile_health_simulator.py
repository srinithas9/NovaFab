
from collections import Counter
from datetime import date, timedelta

from scripts.generate_data.health_simulator import HealthSimulator


SIMULATION_START = date(2026, 1, 1)
SIMULATION_END = date(2026, 9, 30)


simulator = HealthSimulator(seed=42)

health = simulator.initialize_machine()

state_counts = Counter()
scores = []

current_date = SIMULATION_START

while current_date <= SIMULATION_END:

    simulator.update(
        health,
        maintenance_completed=False,
    )

    state_counts[health.state.value] += 1
    scores.append(health.score)

    current_date += timedelta(days=1)


print("=" * 60)
print("HEALTH SIMULATOR PROFILE")
print("=" * 60)

print(f"Initial health score: {scores[0]:.3f}")
print(f"Final health score:   {scores[-1]:.3f}")
print(f"Minimum health score: {min(scores):.3f}")
print(f"Maximum health score: {max(scores):.3f}")

print()
print("Health-state distribution:")

total_days = len(scores)

for state, count in sorted(state_counts.items()):
    percentage = (count / total_days) * 100

    print(
        f"{state:12} "
        f"{count:3} days "
        f"({percentage:5.1f}%)"
    )

