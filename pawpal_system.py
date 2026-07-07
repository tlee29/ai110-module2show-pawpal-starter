"""PawPal+ domain model.

Class skeleton generated from diagrams/uml_draft.mmd.
Four classes: Owner, Pet, Task, Scheduler.
Task and Pet are dataclasses to keep the object definitions clean.
Method bodies are stubs (raise NotImplementedError) — logic comes next.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """A single pet-care task (feeding, walk, medication, grooming, enrichment)."""

    name: str
    category: str
    duration_minutes: int
    priority: str  # "low" | "medium" | "high"
    frequency: str  # e.g. "daily", "weekly"
    due_time: Optional[str] = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        raise NotImplementedError

    def edit(self, **fields) -> None:
        """Update one or more task attributes."""
        raise NotImplementedError

    def priority_score(self) -> int:
        """Return a numeric score so the Scheduler can sort tasks."""
        raise NotImplementedError


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own list of care tasks."""

    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        raise NotImplementedError

    def update_info(self, **fields) -> None:
        """Update one or more pet attributes."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return this pet's task list."""
        raise NotImplementedError


class Owner:
    """The pet owner: their time budget, preferences, and pets."""

    def __init__(
        self,
        name: str,
        available_minutes_per_day: int,
        preferences: Optional[list[str]] = None,
    ) -> None:
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences: list[str] = preferences or []
        self.pets: list[Pet] = []

    def update_available_time(self, minutes: int) -> None:
        """Change how many minutes per day the owner has available."""
        raise NotImplementedError

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's scheduling preferences."""
        raise NotImplementedError

    def view_daily_schedule(self):
        """Return the generated daily schedule for this owner."""
        raise NotImplementedError


class Scheduler:
    """Builds and explains a daily care plan from tasks, time, and preferences."""

    def __init__(
        self,
        available_minutes: int,
        tasks: list[Task],
        preferences: Optional[list[str]] = None,
    ) -> None:
        self.available_minutes = available_minutes
        self.tasks = tasks
        self.preferences: list[str] = preferences or []

    def prioritize_tasks(self) -> list[Task]:
        """Return tasks ordered by priority (and preferences)."""
        raise NotImplementedError

    def generate_schedule(self):
        """Select and order tasks that fit the available time; return the plan."""
        raise NotImplementedError

    def fits_time_budget(self, task: Task, remaining: int) -> bool:
        """Return True if the task fits within the remaining minutes."""
        raise NotImplementedError

    def explain_decisions(self) -> list[str]:
        """Return human-readable reasons for why each task was chosen or skipped."""
        raise NotImplementedError
