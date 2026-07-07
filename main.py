"""Terminal demo for PawPal+ logic, with friendly, color-coded output.

Formatting libraries:
- tabulate  -> structured, aligned CLI tables
- colorama  -> cross-platform ANSI colors (works on Windows terminals too)
Emojis flag task categories and status at a glance.
"""

import sys

# 1. Import the classes from pawpal_system.py
from colorama import Fore, Style, init as colorama_init
from tabulate import tabulate

from pawpal_system import Owner, Pet, Task, Scheduler

# Windows terminals default to cp1252, which can't encode emojis — force UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Reset colors automatically after every print; strip codes if piped to a file.
colorama_init(autoreset=True)

# Emoji per task category (falls back to a generic pin for unknown types).
CATEGORY_EMOJI = {
    "walk": "🐕",
    "feeding": "🍽️",
    "medication": "💊",
    "grooming": "🛁",
    "enrichment": "🎾",
    "medical": "🩺",
    "care": "🐾",
}
# Color per priority label.
PRIORITY_COLOR = {
    "high": Fore.RED,
    "medium": Fore.YELLOW,
    "low": Fore.GREEN,
}


def category_icon(category: str) -> str:
    """Return an emoji for a task category (📌 if unrecognized)."""
    return CATEGORY_EMOJI.get(category.lower(), "📌")


def color_priority(priority: str) -> str:
    """Color a priority label red/yellow/green by urgency."""
    color = PRIORITY_COLOR.get(priority.lower(), "")
    return f"{color}{priority}{Style.RESET_ALL}"


def status_badge(completed: bool) -> str:
    """Green ✅ for done, dim ⏳ for pending."""
    return f"{Fore.GREEN}✅ done{Style.RESET_ALL}" if completed \
        else f"{Style.DIM}⏳ pending{Style.RESET_ALL}"


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

    print(f"\n{Style.BRIGHT}🕒 All tasks, sorted by time (sort_by_time){Style.RESET_ALL}")
    sorted_rows = [
        [
            t.due_time or "--:--",
            f"{category_icon(t.category)} {t.name}",
            t.pet_name,
            color_priority(t.priority),
            status_badge(t.completed),
        ]
        for t in scheduler.sort_by_time()
    ]
    print(tabulate(
        sorted_rows,
        headers=["Time", "Task", "Pet", "Priority", "Status"],
        tablefmt="rounded_outline",
    ))

    print(f"\n{Style.BRIGHT}🏅 Priority-first order "
          f"(sort_by_priority_then_time){Style.RESET_ALL}")
    prio_rows = [
        [
            color_priority(t.priority),
            t.due_time or "--:--",
            f"{category_icon(t.category)} {t.name}",
            t.pet_name,
        ]
        for t in scheduler.sort_by_priority_then_time()
    ]
    print(tabulate(
        prio_rows,
        headers=["Priority", "Time", "Task", "Pet"],
        tablefmt="rounded_outline",
    ))

    print(f"\n{Style.BRIGHT}🔍 Filters (filter_tasks){Style.RESET_ALL}")
    pending = [t.name for t in scheduler.filter_tasks(status="pending")]
    completed = [t.name for t in scheduler.filter_tasks(status="completed")]
    mochi = [t.name for t in scheduler.filter_tasks(pet_name="Mochi")]
    print(f"  {Fore.CYAN}pending:{Style.RESET_ALL}   {', '.join(pending) or '—'}")
    print(f"  {Fore.CYAN}completed:{Style.RESET_ALL} {', '.join(completed) or '—'}")
    print(f"  {Fore.CYAN}Mochi's:{Style.RESET_ALL}   {', '.join(mochi) or '—'}")

    print(f"\n{Style.BRIGHT}⚠️  Conflict check (conflict_warnings){Style.RESET_ALL}")
    warnings = scheduler.conflict_warnings()
    if warnings:
        for w in warnings:
            print(f"  {Fore.RED}{w}{Style.RESET_ALL}")
    else:
        print(f"  {Fore.GREEN}✅ No time conflicts.{Style.RESET_ALL}")


def print_schedule(owner, plan, start_hour: int = 8) -> None:
    """Print a plan as a color-coded, emoji-tagged table for the terminal."""
    print(f"\n{Style.BRIGHT}🐾 Today's Schedule for {owner.name}{Style.RESET_ALL} "
          f"(budget: {owner.available_minutes_per_day} min)")

    # Walk a running clock, advancing by each task's duration.
    rows = []
    minutes = start_hour * 60
    for task in plan.scheduled:
        clock = f"{minutes // 60:02d}:{minutes % 60:02d}"
        rows.append([
            clock,
            f"{category_icon(task.category)} {task.name}",
            task.pet_name,
            f"{task.duration_minutes} min",
            color_priority(task.priority),
        ])
        minutes += task.duration_minutes

    if rows:
        print(tabulate(
            rows,
            headers=["Time", "Task", "Pet", "Duration", "Priority"],
            tablefmt="rounded_outline",
        ))
    else:
        print(f"{Style.DIM}  (nothing scheduled today){Style.RESET_ALL}")

    if plan.skipped:
        print(f"\n{Fore.YELLOW}⚠️  Skipped (no time left):{Style.RESET_ALL}")
        skipped_rows = [
            [f"{category_icon(t.category)} {t.name}", t.pet_name, f"{t.duration_minutes} min"]
            for t in plan.skipped
        ]
        print(tabulate(skipped_rows, headers=["Task", "Pet", "Duration"],
                       tablefmt="rounded_outline"))

    print(f"\n{Style.BRIGHT}📊 {plan.summary()}{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
