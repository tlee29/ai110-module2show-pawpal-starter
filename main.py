"""Temporary testing ground for PawPal+ logic.
"""

# 1. Import the classes from pawpal_system.py
from pawpal_system import Owner, Pet, Task


def main() -> None:
    # 2. Create an Owner and at least two Pets.
    owner = Owner(
        name="Jordan",
        available_minutes_per_day=60,
        preferences=["medication", "morning walk"],
    )

    mochi = Pet(name="Mochi", species="dog", breed="Shiba", age=3)
    luna = Pet(name="Luna", species="cat", breed="Tabby", age=5)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 3. Add at least three Tasks with different durations to those pets.
    mochi.add_task(Task("Morning walk", "walk", duration_minutes=30, priority="high"))
    mochi.add_task(Task("Give meds", "medication", duration_minutes=5, priority="low"))
    luna.add_task(Task("Feed", "feeding", duration_minutes=10, priority="high"))
    luna.add_task(Task("Play", "enrichment", duration_minutes=20, priority="medium"))

    # 4. Build and print "Today's Schedule".
    plan = owner.view_daily_schedule()
    print_schedule(owner, plan)


def print_schedule(owner, plan, start_hour: int = 8) -> None:
    """Print a plan as a clean, time-slotted agenda for the terminal."""
    width = 44
    print()
    print("=" * width)
    print(f" Today's Schedule for {owner.name}".ljust(width))
    print(f" Time budget: {owner.available_minutes_per_day} min".ljust(width))
    print("=" * width)

    # Walk a running clock, advancing by each task's duration.
    minutes = start_hour * 60
    for task in plan.scheduled:
        clock = f"{minutes // 60:02d}:{minutes % 60:02d}"
        label = f"{task.name} ({task.pet_name})"
        print(f" {clock}  {label:<28}{task.duration_minutes:>3} min")
        minutes += task.duration_minutes

    if plan.skipped:
        print("-" * width)
        print(" Skipped (no time left):")
        for task in plan.skipped:
            label = f"{task.name} ({task.pet_name})"
            print(f"        {label:<28}{task.duration_minutes:>3} min")

    print("=" * width)
    print(f" {plan.summary()}")
    print("=" * width)


if __name__ == "__main__":
    main()
