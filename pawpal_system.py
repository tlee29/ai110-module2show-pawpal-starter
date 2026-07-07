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

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

# Default file the Owner persists to / loads from between runs.
DATA_FILE = "data.json"

# Priority label -> base numeric score (higher = scheduled first).
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3}
# Extra score added when a task matches one of the owner's preferences.
PREFERENCE_BONUS = 2
# How many days forward each frequency repeats (None => one-off, no repeat).
RECURRENCE_DAYS = {"daily": 1, "weekly": 7, "biweekly": 14, "monthly": 30}


def _parse_hhmm(clock: str) -> Optional[int]:
    """Parse an 'HH:MM' string into minutes since midnight, or None if invalid."""
    try:
        hours, minutes = clock.split(":")
        total = int(hours) * 60 + int(minutes)
    except (ValueError, AttributeError):
        return None
    return total if 0 <= total < 24 * 60 else None


@dataclass
class Task:
    """A single pet-care task (feeding, walk, medication, grooming, enrichment)."""

    name: str
    category: str
    duration_minutes: int
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "daily"  # "daily" | "weekly" | "biweekly" | "monthly"
    due_time: Optional[str] = None  # "HH:MM" clock time this task should start
    due_date: Optional[date] = None  # calendar day this occurrence is due
    completed: bool = False
    pet_name: Optional[str] = None  # set when attached to a Pet
    anchor_day: int = 0  # day_index this recurring task first fires on

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

    def start_minutes(self) -> Optional[int]:
        """Parse `due_time` ("HH:MM") into minutes since midnight, or None."""
        if not self.due_time:
            return None
        return _parse_hhmm(self.due_time)

    def end_minutes(self) -> Optional[int]:
        """When this task finishes, in minutes since midnight, or None."""
        start = self.start_minutes()
        return None if start is None else start + self.duration_minutes

    def is_due_today(self, day_index: int = 0) -> bool:
        """Whether this task should run on the given day.

        Recurrence is anchored to `anchor_day`, so weekly/biweekly/monthly
        tasks spread across the calendar instead of all firing on day 0:
          daily    -> every day
          weekly   -> every 7 days from anchor_day
          biweekly -> every 14 days from anchor_day
          monthly  -> every 30 days from anchor_day
        Completed tasks are never due again.
        """
        if self.completed:
            return False
        offset = day_index - self.anchor_day
        if offset < 0:
            return False  # not started yet
        step = RECURRENCE_DAYS.get(self.frequency.lower())
        if step is None:
            return True  # unknown frequency: treat as due
        return offset % step == 0

    def next_occurrence(self) -> Optional["Task"]:
        """Return a fresh, incomplete copy of this task for its next date.

        The new due_date is this occurrence's date (or today, if unset) plus
        the frequency interval, e.g. daily -> today + timedelta(days=1).
        Returns None for one-off / unknown frequencies (nothing to repeat).
        """
        step = RECURRENCE_DAYS.get(self.frequency.lower())
        if step is None:
            return None  # not a recurring task
        base = self.due_date or date.today()
        return replace(
            self,
            due_date=base + timedelta(days=step),
            completed=False,
        )

    def to_dict(self) -> dict:
        """Serialize to a JSON-safe dict (`due_date` -> ISO string)."""
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat() if self.due_date else None
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from a dict produced by `to_dict` (parse `due_date`)."""
        data = dict(data)  # don't mutate the caller's dict
        raw_date = data.get("due_date")
        data["due_date"] = date.fromisoformat(raw_date) if raw_date else None
        return cls(**data)


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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task done and auto-add its next occurrence if it recurs.

        Returns the newly created next-occurrence Task (already attached to
        this pet), or None if the task was one-off / non-recurring.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.add_task(next_task)  # re-stamps pet_name and appends
        return next_task

    def update_info(self, **fields) -> None:
        """Update one or more pet attributes by name."""
        for key, value in fields.items():
            if not hasattr(self, key):
                raise AttributeError(f"Pet has no attribute {key!r}")
            setattr(self, key, value)

    def get_tasks(self) -> list[Task]:
        """Return this pet's task list."""
        return self.tasks

    def to_dict(self) -> dict:
        """Serialize this pet and its tasks to a JSON-safe dict."""
        return {
            "name": self.name,
            "species": self.species,
            "breed": self.breed,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet (and its Tasks) from a dict produced by `to_dict`."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed", ""),
            age=data.get("age", 0),
        )
        for task_data in data.get("tasks", []):
            pet.tasks.append(Task.from_dict(task_data))
        return pet


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

    # --- persistence ----------------------------------------------------

    def to_dict(self) -> dict:
        """Serialize the whole owner graph (pets + tasks) to a JSON-safe dict."""
        return {
            "name": self.name,
            "available_minutes_per_day": self.available_minutes_per_day,
            "preferences": self.preferences,
            "pets": [pet.to_dict() for pet in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner (with pets and tasks) from a serialized dict."""
        owner = cls(
            name=data["name"],
            available_minutes_per_day=data["available_minutes_per_day"],
            preferences=data.get("preferences", []),
        )
        for pet_data in data.get("pets", []):
            owner.pets.append(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str = DATA_FILE) -> None:
        """Write this owner (and all pets/tasks) to `path` as JSON."""
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2), encoding="utf-8"
        )

    @classmethod
    def load_from_json(cls, path: str = DATA_FILE) -> Optional["Owner"]:
        """Load an Owner from `path`, or return None if the file doesn't exist.

        Returning None (rather than raising) lets the app fall back to a fresh
        owner on first run, before any data has been saved.
        """
        file = Path(path)
        if not file.exists():
            return None
        return cls.from_dict(json.loads(file.read_text(encoding="utf-8")))


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

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> list[Task]:
        """Filter the task pool by any combination of pet, status, category.

        status: "pending" | "completed" | "done" (or None for all).
        Omitted arguments are ignored, so filter_tasks() returns everything.
        """
        result = self.tasks
        if pet_name is not None:
            result = [t for t in result if t.pet_name == pet_name]
        if status is not None:
            want_done = status.lower() in ("completed", "done")
            result = [t for t in result if t.completed == want_done]
        if category is not None:
            key = category.lower()
            result = [t for t in result if t.category.lower() == key]
        return list(result)

    def sort_by_time(self, candidates: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks ordered by clock time (earliest `due_time` first).

        Uses a lambda key on the "HH:MM" string. Zero-padded 24-hour strings
        sort lexicographically in the same order as chronologically, so plain
        string comparison works. Tasks with no `due_time` fall back to "99:99"
        so they sort to the end.
        """
        pool = candidates if candidates is not None else self.tasks
        return sorted(pool, key=lambda t: t.due_time or "99:99")

    def find_conflicts(
        self, candidates: Optional[list[Task]] = None
    ) -> list[tuple[Task, Task]]:
        """Detect timed tasks whose [start, end) windows overlap.

        Only tasks with a valid `due_time` participate. Returns each
        overlapping pair once. Two tasks for different pets still conflict
        because a single owner can't be in two places at once.
        """
        pool = candidates if candidates is not None else self.tasks
        timed = [t for t in pool if t.start_minutes() is not None]
        timed.sort(key=lambda t: t.start_minutes())
        conflicts: list[tuple[Task, Task]] = []
        for i, earlier in enumerate(timed):
            for later in timed[i + 1:]:
                if later.start_minutes() >= earlier.end_minutes():
                    break  # sorted by start: nothing after this overlaps `earlier`
                conflicts.append((earlier, later))
        return conflicts

    def conflict_warnings(
        self, candidates: Optional[list[Task]] = None
    ) -> list[str]:
        """Lightweight check: return a warning string per overlapping pair.

        Returns an empty list when there are no conflicts. Never raises — a
        conflict is reported, not treated as an error, so the caller can print
        the warnings and carry on. Same-pet and cross-pet overlaps both count
        (one owner can't be in two places at once).
        """
        warnings: list[str] = []
        for earlier, later in self.find_conflicts(candidates):
            same = earlier.pet_name == later.pet_name and earlier.pet_name is not None
            who = (
                f"{earlier.pet_name}'s" if same
                else f"{earlier.pet_name or '?'} and {later.pet_name or '?'}"
            )
            warnings.append(
                f"[!] Time conflict for {who} tasks: "
                f"'{earlier.name}' ({earlier.due_time}) overlaps "
                f"'{later.name}' ({later.due_time})."
            )
        return warnings

    def suggest_next_slot(
        self,
        duration_minutes: int,
        earliest: str = "08:00",
        latest: str = "22:00",
        candidates: Optional[list[Task]] = None,
    ) -> Optional[str]:
        """Find the earliest free start time that fits a task of `duration_minutes`.

        Scans the day from `earliest` to `latest`, treating every existing timed
        task as a busy [start, end) block. Returns the first "HH:MM" start where a
        `duration_minutes`-long task fits in a gap without overlapping anything, or
        None if the day is too full. Untimed tasks are ignored (they don't block a
        clock slot). This goes beyond basic scheduling: instead of only *detecting*
        conflicts, it proactively *proposes* a conflict-free time.
        """
        pool = candidates if candidates is not None else self.tasks
        day_start = _parse_hhmm(earliest)
        day_end = _parse_hhmm(latest)
        if day_start is None or day_end is None or duration_minutes <= 0:
            return None

        # Collect busy blocks from timed tasks, sorted by start.
        busy = sorted(
            (t.start_minutes(), t.end_minutes())
            for t in pool
            if t.start_minutes() is not None
        )

        cursor = day_start
        for start, end in busy:
            if end <= cursor:
                continue  # block already behind the cursor
            # Is there room between the cursor and this block starting?
            if start - cursor >= duration_minutes:
                break  # gap found at `cursor`
            cursor = max(cursor, end)  # jump past this block

        if cursor + duration_minutes <= day_end:
            return f"{cursor // 60:02d}:{cursor % 60:02d}"
        return None

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

    def sort_by_priority_then_time(
        self, candidates: Optional[list[Task]] = None
    ) -> list[Task]:
        """Order tasks by priority (highest first), then by clock time.

        This is the "priority-first" view: a high-priority task always precedes
        a medium one regardless of the hour, and tasks sharing a priority fall
        back to earliest `due_time` (untimed tasks last, via the "99:99"
        sentinel). Owner preferences still boost a task's effective priority.
        Unlike `prioritize_tasks()` (which tie-breaks by shortest duration to
        pack the time budget), this method tie-breaks by time for a readable,
        chronological agenda within each priority tier.
        """
        pool = candidates if candidates is not None else self.tasks
        return sorted(
            pool,
            key=lambda t: (-t.priority_score(self.preferences), t.due_time or "99:99"),
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
