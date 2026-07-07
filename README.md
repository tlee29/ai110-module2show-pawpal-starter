# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

============================================
 Today's Schedule for Jordan                
 Time budget: 60 min                        
============================================
 08:00  Morning walk (Mochi)         30 min
 08:30  Give meds (Mochi)             5 min
 08:35  Feed (Luna)                  10 min
--------------------------------------------
 Skipped (no time left):
        Play (Luna)                  20 min
============================================
 3 task(s) scheduled (45 min), 1 skipped
============================================

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All logic lives in `pawpal_system.py`. The scheduler builds a `DailyPlan`
(scheduled tasks, skipped tasks, and a plain-language explanation for each
decision) from an owner's pets, tasks, time budget, and preferences.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority scheduling | `Scheduler.prioritize_tasks()`, `Scheduler.generate_schedule()` | Greedy: sort by priority score (highest first), tie-break by shortest duration, then fill until the time budget is exhausted. |
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by `due_time` using a lambda key on the `"HH:MM"` string (`key=lambda t: t.due_time or "99:99"`); untimed tasks sort last. |
| Filtering | `Scheduler.filter_tasks()`, `pending_tasks()`, `completed_tasks()`, `tasks_for_pet()` | Filter the task pool by pet name, completion status, and/or category — any combination. |
| Conflict detection | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()` | Compares each timed task's `[start, end)` window; overlaps (same pet *or* different pets) are reported as warning strings — never raises. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly`/`biweekly`/`monthly` task auto-creates the next occurrence with its `due_date` advanced via `datetime.timedelta`. |
| Due-today filter | `Task.is_due_today()` | Anchored to `anchor_day` so recurring tasks fire on their own cadence instead of all on day 0. |
| Time helpers | `Task.start_minutes()`, `Task.end_minutes()` | Parse `"HH:MM"` into minutes-since-midnight for sorting and overlap math. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
