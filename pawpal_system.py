"""PawPal+ domain model.

Four classes: Owner, Pet, Task, Scheduler (+ a small DailyPlan result holder).
Task and Pet are dataclasses to keep the object definitions clean.

Design notes (revised after skeleton review):
- Task carries `pet_name` so a scheduled task can name its pet in a multi-pet plan.
- Task.is_due_today() uses `frequency` so weekly tasks aren't scheduled every day.
- Scheduler returns a single DailyPlan holding both the ordered tasks AND the
  per-task explanations (why chosen / why skipped) — computed together in one pass.
- Owner preferences (e.g. "medication", "morning walks") boost matching tasks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Priority label -> base numeric score (higher = scheduled first).
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
# Extra score added when a task matches one of the owner's preferences.
PREFERENCE_BONUS = 2


@dataclass
class Task:
    """A single pet-care task (feeding, walk, medication, grooming, enrichment)."""

    name: str
    category: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "daily"  # "daily" | "weekly"
    due_time: Optional[str] = None
    completed: bool = False
    pet_name: Optional[str] = None  # set when attached to a Pet

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def edit(self, **fields) -> None:
        """Update one or more task attributes by name."""
        for key, value in fields.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            setattr(self, key, value)

    def priority_score(self, preferences: Optional[list[str]] = None) -> int:
        """Numeric sort key. Base priority + a bonus if it matches a preference."""
        score = PRIORITY_SCORES.get(self.priority.lower(), 0)
        if preferences:
            text = f"{self.name} {self.category}".lower()
            if any(pref.lower() in text for pref in preferences):
                score += PREFERENCE_BONUS
        return score

    def is_due_today(self, day_index: int = 0) -> bool:
        """Whether this task should run today.

        daily -> every day; weekly -> once per 7-day cycle (day_index % 7 == 0).
        Completed tasks are never due again.
        """
        if self.completed:
            return False
        freq = self.frequency.lower()
        if freq == "daily":
            return True
        if freq == "weekly":
            return day_index % 7 == 0
        return True  # unknown frequency: treat as due


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and stamp it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        self.tasks.remove(task)

    def update_info(self, **fields) -> None:
        """Update one or more pet attributes by name."""
        for key, value in fields.items():
            if not hasattr(self, key):
                raise AttributeError(f"Pet has no attribute {key!r}")
            setattr(self, key, value)

    def get_tasks(self) -> list[Task]:
        """Return this pet's task list."""
        return self.tasks


@dataclass
class DailyPlan:
    """Result of a scheduling run: what got scheduled, what didn't, and why."""

    scheduled: list[Task] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)
    explanations: list[str] = field(default_factory=list)
    total_minutes: int = 0

    def summary(self) -> str:
        """One-line human summary of the plan."""
        return (
            f"{len(self.scheduled)} task(s) scheduled "
            f"({self.total_minutes} min), {len(self.skipped)} skipped"
        )


class Owner:
    """The pet owner: their time budget, preferences, and pets."""

    def __init__(
        self,
        name: str,
        available_minutes_per_day: int,
        preferences: Optional[list[str]] = None,
    ) -> None:
        """Create an owner with a daily time budget and optional preferences."""
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def update_available_time(self, minutes: int) -> None:
        """Change how many minutes per day the owner has available."""
        if minutes < 0:
            raise ValueError("available minutes cannot be negative")
        self.available_minutes_per_day = minutes

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's scheduling preferences."""
        self.preferences = list(preferences)

    def all_tasks(self) -> list[Task]:
        """Flatten tasks across every pet the owner has."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def view_daily_schedule(self, day_index: int = 0) -> DailyPlan:
        """Build a Scheduler from this owner's data and return today's plan."""
        scheduler = Scheduler(
            available_minutes=self.available_minutes_per_day,
            tasks=self.all_tasks(),
            preferences=self.preferences,
        )
        return scheduler.generate_schedule(day_index=day_index)


class Scheduler:
    """Builds a daily care plan from tasks, time budget, and preferences."""

    def __init__(
        self,
        available_minutes: int,
        tasks: list[Task],
        preferences: Optional[list[str]] = None,
    ) -> None:
        """Create a scheduler over a task pool with a time budget and prefs."""
        self.available_minutes = available_minutes
        self.tasks = tasks
        self.preferences: list[str] = preferences or []

    @classmethod
    def from_owner(cls, owner: "Owner") -> "Scheduler":
        """Build a Scheduler directly from an Owner's time, tasks, and prefs."""
        return cls(
            available_minutes=owner.available_minutes_per_day,
            tasks=owner.all_tasks(),
            preferences=owner.preferences,
        )

    # --- retrieval / management across all pets -------------------------

    def pending_tasks(self) -> list[Task]:
        """All not-yet-completed tasks the scheduler knows about."""
        return [t for t in self.tasks if not t.completed]

    def completed_tasks(self) -> list[Task]:
        """All tasks already marked done."""
        return [t for t in self.tasks if t.completed]

    def tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Filter the pool down to one pet's tasks."""
        return [t for t in self.tasks if t.pet_name == pet_name]

    def complete_task(self, name: str, pet_name: Optional[str] = None) -> bool:
        """Mark the first matching task complete. Returns True if one was found.

        Pass `pet_name` to disambiguate when two pets share a task name.
        """
        for task in self.tasks:
            if task.name == name and (pet_name is None or task.pet_name == pet_name):
                task.mark_complete()
                return True
        return False

    def prioritize_tasks(self, candidates: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks ordered by score (desc), then shorter duration first.

        Shorter-first as a tiebreak lets more tasks fit in the same budget.
        """
        pool = candidates if candidates is not None else self.tasks
        return sorted(
            pool,
            key=lambda t: (-t.priority_score(self.preferences), t.duration_minutes),
        )

    def fits_time_budget(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits within the remaining minutes."""
        return task.duration_minutes <= remaining

    def generate_schedule(self, day_index: int = 0) -> DailyPlan:
        """Greedily select the highest-priority tasks that fit the time budget.

        Returns a DailyPlan with scheduled/skipped tasks and an explanation
        for each decision — all computed in a single pass.
        """
        plan = DailyPlan()
        # Filter to tasks actually due today before prioritizing.
        due = [t for t in self.tasks if t.is_due_today(day_index)]
        remaining = self.available_minutes

        for task in self.prioritize_tasks(due):
            who = f" for {task.pet_name}" if task.pet_name else ""
            if self.fits_time_budget(task, remaining):
                plan.scheduled.append(task)
                remaining -= task.duration_minutes
                plan.total_minutes += task.duration_minutes
                plan.explanations.append(
                    f"Scheduled '{task.name}'{who} "
                    f"({task.duration_minutes} min, {task.priority} priority); "
                    f"{remaining} min left."
                )
            else:
                plan.skipped.append(task)
                plan.explanations.append(
                    f"Skipped '{task.name}'{who} "
                    f"({task.duration_minutes} min) — only {remaining} min left."
                )
        return plan
