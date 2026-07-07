"""Basic tests for PawPal+ core behaviors.

Run from the project folder:

    pytest tests_test_pawpal.py
"""

from pawpal_system import Pet, Task


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
