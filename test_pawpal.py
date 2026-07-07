"""Basic tests for PawPal+ core behaviors.

Run from the project folder:

    pytest tests_test_pawpal.py
"""

from pawpal_system import Pet, Scheduler, Task


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
