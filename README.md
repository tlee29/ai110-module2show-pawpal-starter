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
```
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
```
## 🧪 Testing PawPal+

```bash
# Run the full test suite (from this folder):
python -m pytest


# Run with coverage:
pytest --cov
```

**What the 13 tests cover** (`test_pawpal.py`):

- **Task basics** — `mark_complete()` flips the status flag; `Pet.add_task()` grows the task list.
- **Sorting correctness** — `sort_by_time()` returns tasks in strict chronological order by `due_time`, with untimed tasks sorted last.
- **Filtering** — `filter_tasks()` narrows the pool by pet name and completion status, alone or combined.
- **Recurrence logic** — completing a `daily` task spawns a fresh, incomplete occurrence dated the following day (re-attached to the same pet); a one-off task spawns nothing. `is_due_today()` fires daily tasks every day and weekly tasks only on their `anchor_day` cadence.
- **Conflict detection** — `find_conflicts()` flags overlapping and identical-time tasks, ignores back-to-back tasks that merely touch at the boundary, and `conflict_warnings()` reports cross-pet overlaps (one owner can't be in two places at once).

Sample test output:

```
platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Desktop\python-primer\ai110-module2show-pawpal-starter
plugins: anyio-4.9.0
collected 13 items

test_pawpal.py .............                                             [100%]

============================= 13 passed in 0.04s ==============================
```
Confidence level: 5

## 📐 Smarter Scheduling

All logic lives in `pawpal_system.py`. The scheduler builds a `DailyPlan`
(scheduled tasks, skipped tasks, and a plain-language explanation for each
decision) from an owner's pets, tasks, time budget, and preferences.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority scheduling | `Scheduler.prioritize_tasks()`, `Scheduler.generate_schedule()` | Greedy: sort by priority score (highest first), tie-break by shortest duration, then fill until the time budget is exhausted. |
| Sort by time | `Scheduler.sort_by_time()` | Orders tasks by `due_time` using a lambda key on the `"HH:MM"` string (`key=lambda t: t.due_time or "99:99"`); untimed tasks sort last. |
| Priority-first sort | `Scheduler.sort_by_priority_then_time()` | Orders by priority score (highest first), then earliest `due_time` as the tiebreak — a readable agenda where high-priority tasks always lead. |
| Filtering | `Scheduler.filter_tasks()`, `pending_tasks()`, `completed_tasks()`, `tasks_for_pet()` | Filter the task pool by pet name, completion status, and/or category — any combination. |
| Conflict detection | `Scheduler.find_conflicts()`, `Scheduler.conflict_warnings()` | Compares each timed task's `[start, end)` window; overlaps (same pet *or* different pets) are reported as warning strings — never raises. |
| Recurring tasks | `Task.next_occurrence()`, `Pet.complete_task()` | Completing a `daily`/`weekly`/`biweekly`/`monthly` task auto-creates the next occurrence with its `due_date` advanced via `datetime.timedelta`. |
| Due-today filter | `Task.is_due_today()` | Anchored to `anchor_day` so recurring tasks fire on their own cadence instead of all on day 0. |
| Time helpers | `Task.start_minutes()`, `Task.end_minutes()` | Parse `"HH:MM"` into minutes-since-midnight for sorting and overlap math. |
| Next available slot *(stretch)* | `Scheduler.suggest_next_slot()` | Scans the day as busy `[start, end)` blocks and returns the earliest gap a new task of a given length fits into — proposing a conflict-free time instead of only detecting clashes. |

## 💾 Data Persistence

PawPal+ remembers your pets and tasks between runs by saving them to a
**`data.json`** file in the project folder.

**How it works**

- Serialization uses **custom dictionary conversion** (no external library). Each
  domain class has a `to_dict()` / `from_dict()` pair: `Task` ↔ dict (converting
  its `due_date` to/from an ISO string, since `datetime.date` isn't JSON-native),
  `Pet` nests its tasks, and `Owner` nests its pets — so one call serializes the
  whole object graph.
- **`Owner.save_to_json(path="data.json")`** writes the owner (with all pets and
  tasks) to disk as indented JSON.
- **`Owner.load_from_json(path="data.json")`** reads it back into a live `Owner`,
  or returns `None` if the file doesn't exist yet (so the first run starts fresh
  instead of crashing).

**Workflow**

1. On launch, `app.py` calls `Owner.load_from_json()` — if `data.json` exists your
   data is restored; otherwise a default owner is created.
2. Add pets and tasks as usual.
3. Click **💾 Save data** to write the current state to `data.json`.
4. Next run, everything you saved is loaded automatically.

**Files modified for persistence**

- `pawpal_system.py` — added `to_dict()`/`from_dict()` to `Task`, `Pet`, and
  `Owner`, plus `Owner.save_to_json()` / `load_from_json()` and a `DATA_FILE`
  constant.
- `app.py` — restores from `data.json` on first load and adds a **Save data** button.
- `test_pawpal.py` — added a save/load round-trip test and a missing-file test.
- `.gitignore` — ignores `data.json` (local user data, not source).

## 📸 Demo Walkthrough

### What the app lets you do

The Streamlit app (`app.py`) is organized top-to-bottom as a single interactive page:

- **Owner settings** — edit the owner's name and daily time budget (minutes/day).
- **Add a Pet** — a form to register a pet (name, species, breed, age).
- **Schedule a Task** — attach a task to a pet with a title, category, duration,
  priority, and frequency. An optional **"Set a start time"** toggle adds a clock
  time, which is what unlocks time-sorting and conflict checks.
- **Per-pet task tables** — each pet expands to a table of its tasks (time, minutes,
  priority, frequency, done).
- **Build Schedule** — one button turns everything into today's plan.

### Example workflow

1. **Set the budget** — Owner "Jordan", 60 minutes available today.
2. **Add pets** — add *Mochi* (dog) and *Luna* (cat).
3. **Schedule tasks** — e.g. Mochi's "Evening walk" (30 min, high, 18:00) and
   "Midday pill" (5 min, high, 12:05); Luna's "Lunch feed" (10 min, high, 12:00)
   and "Play" (20 min, medium, no time).
4. **Generate schedule** — click **Build Schedule** to see today's plan.

### Key Scheduler behaviors you'll see

- **Priority + budget fit** — high-priority tasks are chosen first and packed until
  the 60-minute budget runs out; "Play" gets pushed to **Skipped (no time left)**.
- **Sorting by time** — the scheduled table is re-ordered earliest-first by
  `due_time` (untimed tasks sink to the bottom).
- **Conflict warnings** — Luna's "Lunch feed" (12:00) and Mochi's "Midday pill"
  (12:05) overlap, so the app raises an amber **⚠️ conflict** warning with the exact
  overlap window; when nothing clashes it shows a green **✅ No time conflicts**.
- **Explainable plan** — an expander lists *why* each task was scheduled or skipped.

### Sample CLI output (`python main.py`)

`main.py` is a terminal harness that exercises the same logic without Streamlit,
with color-coded, emoji-tagged tables (colors shown live in a real terminal):

```text
🐾 Today's Schedule for Jordan (budget: 60 min)
╭────────┬─────────────────┬───────┬────────────┬────────────╮
│ Time   │ Task            │ Pet   │ Duration   │ Priority   │
├────────┼─────────────────┼───────┼────────────┼────────────┤
│ 08:00  │ 💊 Midday pill  │ Mochi │ 5 min      │ high       │
│ 08:05  │ 🍽️ Lunch feed   │ Luna  │ 10 min     │ high       │
│ 08:15  │ 🐕 Evening walk │ Mochi │ 30 min     │ high       │
╰────────┴─────────────────┴───────┴────────────┴────────────╯

⚠️  Skipped (no time left):
╭─────────┬───────┬────────────╮
│ Task    │ Pet   │ Duration   │
├─────────┼───────┼────────────┤
│ 🎾 Play │ Luna  │ 20 min     │
╰─────────┴───────┴────────────╯

📊 3 task(s) scheduled (45 min), 1 skipped

🕒 All tasks, sorted by time (sort_by_time)
╭────────┬─────────────────┬───────┬────────────┬────────────╮
│ Time   │ Task            │ Pet   │ Priority   │ Status     │
├────────┼─────────────────┼───────┼────────────┼────────────┤
│ 08:00  │ 💊 Give meds    │ Mochi │ low        │ ✅ done    │
│ 12:00  │ 🍽️ Lunch feed   │ Luna  │ high       │ ⏳ pending │
│ 12:05  │ 💊 Midday pill  │ Mochi │ high       │ ⏳ pending │
│ 18:00  │ 🐕 Evening walk │ Mochi │ high       │ ⏳ pending │
│ --:--  │ 🎾 Play         │ Luna  │ medium     │ ⏳ pending │
╰────────┴─────────────────┴───────┴────────────┴────────────╯

🔍 Filters (filter_tasks)
  pending:   Evening walk, Midday pill, Lunch feed, Play
  completed: Give meds
  Mochi's:   Evening walk, Give meds, Midday pill

⚠️  Conflict check (conflict_warnings)
  [!] Time conflict for Luna and Mochi tasks: 'Lunch feed' (12:00) overlaps 'Midday pill' (12:05).
```

> Note: the agenda's left column is a running clock starting at 08:00 (each task
> stacked after the previous one), while `sort_by_time` above shows the tasks'
> actual `due_time` order — which is why the two time columns differ.

### 🏅 Priority-Based Scheduling

Beyond simple time sorting, tasks carry a **priority** (`low` / `medium` / `high`)
and the scheduler can order **priority first, then time** via
`Scheduler.sort_by_priority_then_time()`. A high-priority task precedes a lower
one regardless of the hour; tasks sharing a priority fall back to earliest
`due_time` (untimed tasks last).

**Plain time sort** (`sort_by_time`) — ignores priority entirely:

```text
06:00  Tidy up      (low)
08:00  Morning walk (high)
12:00  Feed         (medium)
20:00  Give meds    (high)
```

**Priority-first sort** (`sort_by_priority_then_time`) — highs rise to the top,
ties broken by time:

```text
high    08:00  Morning walk
high    20:00  Give meds
medium  12:00  Feed
low     06:00  Tidy up      ← earliest clock time, but scheduled last
```

Notice `Tidy up` has the earliest time (06:00) yet lands last because it's low
priority — that's the enhancement over plain time sorting.

**Preferences can boost priority.** In `main.py` the owner prefers `"medication"`,
which adds +2 to matching tasks. That's why the live output ranks a *low*-priority
medication task up with the *high* ones:

```text
🏅 Priority-first order (sort_by_priority_then_time)
╭────────────┬────────┬─────────────────┬───────╮
│ Priority   │ Time   │ Task            │ Pet   │
├────────────┼────────┼─────────────────┼───────┤
│ high       │ 12:05  │ 💊 Midday pill  │ Mochi │
│ low        │ 08:00  │ 💊 Give meds    │ Mochi │   ← low, but +2 "medication" boost
│ high       │ 12:00  │ 🍽️ Lunch feed   │ Luna  │
│ high       │ 18:00  │ 🐕 Evening walk │ Mochi │
│ medium     │ --:--  │ 🎾 Play         │ Luna  │
╰────────────┴────────┴─────────────────┴───────╯
```

> The greedy day-planner (`generate_schedule`) uses a *different* tiebreak —
> shortest-duration-first — so it can fit the most tasks into the time budget.
> `sort_by_priority_then_time()` is the readable agenda view; `prioritize_tasks()`
> is the budget-packing view.

### 🎨 CLI Formatting Features

The terminal demo (`main.py`) uses two small libraries plus emoji to make the
output scannable:

| Feature | How | Library / function |
|---------|-----|--------------------|
| **Structured tables** | Aligned, boxed tables for the schedule, skipped list, and sorted view | `tabulate(rows, headers=..., tablefmt="rounded_outline")` |
| **Color-coded priority** | high = red, medium = yellow, low = green | `colorama` `Fore.*` via `color_priority()` |
| **Status badges** | ✅ done (green) / ⏳ pending (dim) | `colorama` via `status_badge()` |
| **Category emojis** | 🐕 walk · 🍽️ feeding · 💊 medication · 🛁 grooming · 🎾 enrichment · 🩺 medical · 🐾 care · 📌 other | `CATEGORY_EMOJI` dict via `category_icon()` |
| **Conflict highlighting** | conflicts printed in red, "no conflicts" in green | `colorama` `Fore.RED` / `Fore.GREEN` |
| **Auto color reset** | colors reset after each print; stripped automatically when piped to a file | `colorama.init(autoreset=True)` |
| **Emoji-safe output** | forces UTF-8 so emojis render on Windows (cp1252) terminals | `sys.stdout.reconfigure(encoding="utf-8")` |

Install the extras with `pip install -r requirements.txt` (adds `tabulate` and
`colorama`).
