"""Temporary testing ground for PawPal+ logic.
"""

# 1. Import the classes from pawpal_system.py
from pawpal_system import Owner, Pet, Task, Scheduler


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

    # 3. Add tasks DELIBERATELY OUT OF TIME ORDER (18:00 before 08:00, etc.)
    #    so sort_by_time() has something real to reorder.
    mochi.add_task(Task("Evening walk", "walk", 30, priority="high", due_time="18:00"))
    mochi.add_task(Task("Give meds", "medication", 5, priority="low", due_time="08:00",
                        completed=True))
    luna.add_task(Task("Lunch feed", "feeding", 10, priority="high", due_time="12:00"))
    luna.add_task(Task("Play", "enrichment", 20, priority="medium"))  # no due_time

    # Two tasks deliberately overlapping at 12:00 to trigger conflict detection:
    # Luna's "Lunch feed" (12:00-12:10) vs Mochi's "Midday pill" (12:05-12:10).
    mochi.add_task(Task("Midday pill", "medication", 5, priority="high", due_time="12:05"))

    # 4. Build and print "Today's Schedule".
    plan = owner.view_daily_schedule()
    print_schedule(owner, plan)

    # 5. Demonstrate the sorting + filtering methods on the Scheduler.
    demo_sort_and_filter(owner)


def demo_sort_and_filter(owner) -> None:
    """Show sort_by_time() and filter_tasks() working on the owner's tasks."""
    scheduler = Scheduler.from_owner(owner)

    print("\nInsertion order (as added):")
    for t in scheduler.tasks:
        print(f"  {t.due_time or '--:--'}  {t.name}")

    print("\nSorted by time (sort_by_time):")
    for t in scheduler.sort_by_time():
        print(f"  {t.due_time or '--:--'}  {t.name}")

    print("\nFilter — pending only (filter_tasks status='pending'):")
    for t in scheduler.filter_tasks(status="pending"):
        print(f"  {t.name}")

    print("\nFilter — completed only (filter_tasks status='completed'):")
    for t in scheduler.filter_tasks(status="completed"):
        print(f"  {t.name}")

    print("\nFilter — Mochi's tasks (filter_tasks pet_name='Mochi'):")
    for t in scheduler.filter_tasks(pet_name="Mochi"):
        print(f"  {t.name}")

    print("\nConflict check (conflict_warnings):")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  No time conflicts.")


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
