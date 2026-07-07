"""Basic tests for PawPal+ core behaviors.

Run from the project folder:

    pytest test_pawpal.py
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed from False to True."""
    task = Task("Give meds", "medication", duration_minutes=5)

    assert task.completed is False  # tasks start incomplete
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Task Addition: adding a task grows the pet's task list by one."""
    pet = Pet("Mochi", "dog")
    assert len(pet.tasks) == 0  # no tasks yet

    pet.add_task(Task("Morning walk", "walk", duration_minutes=30))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Feed", "feeding", duration_minutes=10))
    assert len(pet.tasks) == 2


# --- Sorting by time -------------------------------------------------------

def test_sort_by_time_orders_by_due_time_untimed_last():
    """Timed tasks come out earliest-first; untimed tasks sink to the end."""
    late = Task("Dinner", "feeding", 10, due_time="18:00")
    early = Task("Breakfast", "feeding", 10, due_time="07:30")
    untimed = Task("Play", "enrichment", 15)
    sched = Scheduler(available_minutes=120, tasks=[late, untimed, early])

    assert sched.sort_by_time() == [early, late, untimed]


# --- Priority-first ordering -----------------------------------------------

def test_sort_by_priority_then_time():
    """High priority always precedes lower; ties fall back to earliest time."""
    low_early = Task("Tidy", "care", 10, priority="low", due_time="06:00")
    high_late = Task("Meds", "medication", 5, priority="high", due_time="20:00")
    high_early = Task("Walk", "walk", 30, priority="high", due_time="08:00")
    med = Task("Feed", "feeding", 10, priority="medium", due_time="12:00")
    sched = Scheduler(
        available_minutes=120, tasks=[low_early, high_late, high_early, med]
    )

    ordered = sched.sort_by_priority_then_time()
    # Both highs first (earliest-time tie-break), then medium, then low —
    # even though low_early has the earliest clock time of all.
    assert ordered == [high_early, high_late, med, low_early]


# --- Filtering by pet / status ---------------------------------------------

def test_filter_tasks_by_pet_and_status():
    """filter_tasks narrows the pool by pet and by completion status."""
    walk = Task("Walk", "walk", 30, pet_name="Mochi")
    meds = Task("Meds", "medication", 5, pet_name="Mochi", completed=True)
    feed = Task("Feed", "feeding", 10, pet_name="Luna")
    sched = Scheduler(available_minutes=120, tasks=[walk, meds, feed])

    assert sched.filter_tasks(pet_name="Mochi") == [walk, meds]
    assert sched.filter_tasks(status="pending") == [walk, feed]
    assert sched.filter_tasks(pet_name="Mochi", status="completed") == [meds]


# --- Recurring tasks -------------------------------------------------------

def test_weekly_task_due_on_anchor_cycle_only():
    """A weekly task fires on its anchor day and every 7 days after."""
    weekly = Task("Bath", "grooming", 20, frequency="weekly", anchor_day=2)

    assert weekly.is_due_today(day_index=2) is True
    assert weekly.is_due_today(day_index=9) is True   # +7
    assert weekly.is_due_today(day_index=3) is False  # off-cycle
    assert weekly.is_due_today(day_index=0) is False  # before anchor


def test_daily_task_due_every_day():
    """A daily task is due every day from its anchor onward."""
    daily = Task("Feed", "feeding", 10)  # anchor_day defaults to 0
    assert all(daily.is_due_today(d) for d in range(5))


# --- Conflict detection ----------------------------------------------------

def test_find_conflicts_detects_overlap():
    """Two timed tasks whose windows overlap are reported as a conflict."""
    walk = Task("Walk", "walk", 60, due_time="08:00")   # 08:00-09:00
    vet = Task("Vet", "medical", 30, due_time="08:30")   # 08:30-09:00 (overlaps)
    feed = Task("Feed", "feeding", 10, due_time="09:30")  # no overlap
    sched = Scheduler(available_minutes=180, tasks=[walk, vet, feed])

    conflicts = sched.find_conflicts()
    assert conflicts == [(walk, vet)]


def test_find_conflicts_ignores_back_to_back():
    """Tasks that touch at the boundary (end == next start) do not conflict."""
    a = Task("A", "walk", 30, due_time="08:00")  # 08:00-08:30
    b = Task("B", "feeding", 10, due_time="08:30")  # starts exactly at A's end
    sched = Scheduler(available_minutes=120, tasks=[a, b])

    assert sched.find_conflicts() == []


# --- Required: Sorting Correctness -----------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Sorting Correctness: tasks come back strictly earliest -> latest."""
    tasks = [
        Task("Dinner", "feeding", 10, due_time="18:00"),
        Task("Lunch", "feeding", 10, due_time="12:15"),
        Task("Breakfast", "feeding", 10, due_time="07:30"),
        Task("Night meds", "medication", 5, due_time="22:45"),
    ]
    sched = Scheduler(available_minutes=240, tasks=tasks)

    ordered_times = [t.due_time for t in sched.sort_by_time()]
    assert ordered_times == ["07:30", "12:15", "18:00", "22:45"]


# --- Required: Recurrence Logic --------------------------------------------

def test_completing_daily_task_creates_next_days_occurrence():
    """Recurrence Logic: completing a daily task spawns one for the next day."""
    pet = Pet("Mochi", "dog")
    today = date.today()
    feed = Task("Feed", "feeding", 10, frequency="daily", due_date=today)
    pet.add_task(feed)

    next_task = pet.complete_task(feed)

    # Original is done; a brand-new, incomplete occurrence now exists.
    assert feed.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.due_date == today + timedelta(days=1)
    # The new occurrence was attached to the same pet.
    assert next_task in pet.tasks
    assert next_task.pet_name == "Mochi"
    assert len(pet.tasks) == 2


def test_completing_one_off_task_creates_no_recurrence():
    """A non-recurring task produces no follow-up when completed."""
    pet = Pet("Luna", "cat")
    once = Task("Vet visit", "medical", 45, frequency="one-off")
    pet.add_task(once)

    assert pet.complete_task(once) is None
    assert len(pet.tasks) == 1  # nothing new was added


# --- Required: Conflict Detection (duplicate times) ------------------------

def test_find_conflicts_flags_identical_times():
    """Conflict Detection: two tasks at the exact same time are flagged."""
    walk = Task("Walk", "walk", 30, due_time="08:00")
    meds = Task("Meds", "medication", 5, due_time="08:00")  # same start time
    sched = Scheduler(available_minutes=120, tasks=[walk, meds])

    conflicts = sched.find_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0] == (walk, meds)


def test_suggest_next_slot_finds_earliest_gap():
    """Stretch: suggest_next_slot proposes the earliest conflict-free start."""
    # Busy 08:00-08:30 and 09:00-10:00; a 30-min task fits at 08:30.
    a = Task("Walk", "walk", 30, due_time="08:00")
    b = Task("Feed", "feeding", 60, due_time="09:00")
    sched = Scheduler(available_minutes=240, tasks=[a, b])

    # First free slot at/after 08:00 for a 30-min task is 08:30 (before b).
    assert sched.suggest_next_slot(30) == "08:30"
    # A 45-min task won't fit in the 30-min gap, so it lands after b at 10:00.
    assert sched.suggest_next_slot(45) == "10:00"


def test_suggest_next_slot_returns_none_when_day_full():
    """No slot fits before the day's end -> returns None."""
    block = Task("All day", "care", 60, due_time="21:30")  # 21:30-22:30
    sched = Scheduler(available_minutes=120, tasks=[block])

    # Only room is 08:00-21:30; a 30-min task fits there, but cap the window tight:
    assert sched.suggest_next_slot(30, earliest="21:45", latest="22:00") is None


def test_conflict_warnings_reports_cross_pet_overlap():
    """A single owner can't serve two pets at once — cross-pet overlaps warn."""
    a = Task("Walk", "walk", 30, due_time="08:00", pet_name="Mochi")
    b = Task("Feed", "feeding", 10, due_time="08:00", pet_name="Luna")
    sched = Scheduler(available_minutes=120, tasks=[a, b])

    warnings = sched.conflict_warnings()
    assert len(warnings) == 1
    assert "Mochi" in warnings[0] and "Luna" in warnings[0]


# --- Persistence (save/load JSON) ------------------------------------------

def test_owner_json_round_trip(tmp_path):
    """Persistence: saving then loading reproduces the owner, pets, and tasks."""
    from datetime import date

    owner = Owner("Jordan", 90, preferences=["medication"])
    pet = Pet("Mochi", "dog", breed="Shiba", age=3)
    pet.add_task(
        Task("Give meds", "medication", 5, priority="high",
             due_time="08:00", due_date=date(2026, 7, 7))
    )
    owner.add_pet(pet)

    path = tmp_path / "data.json"
    owner.save_to_json(str(path))
    loaded = Owner.load_from_json(str(path))

    assert loaded is not None
    assert loaded.name == "Jordan"
    assert loaded.available_minutes_per_day == 90
    assert loaded.preferences == ["medication"]
    assert len(loaded.pets) == 1
    restored_task = loaded.pets[0].tasks[0]
    assert restored_task.name == "Give meds"
    assert restored_task.pet_name == "Mochi"  # stamp survives the round trip
    assert restored_task.due_date == date(2026, 7, 7)  # date parsed back correctly


def test_load_from_json_missing_file_returns_none(tmp_path):
    """Loading a non-existent file returns None so the app can start fresh."""
    assert Owner.load_from_json(str(tmp_path / "nope.json")) is None
