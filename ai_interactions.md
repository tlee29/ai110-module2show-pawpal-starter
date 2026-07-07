# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Across a multi-step session I asked the agent to: (1) suggest edge cases for the
scheduler and draft a `pytest` suite; (2) wire the `Scheduler` methods (sorting,
conflict warnings) into the Streamlit UI; (3) sync the UML diagram to the final
code; (4) write the README Features + Demo Walkthrough and parts of the
reflection; and (5) add a stretch algorithm beyond the basic requirements.

**Files modified**

- `test_pawpal.py` — added 15 tests (sorting, recurrence, conflict, next-slot).
- `app.py` — added a start-time input, a conflict table, and time-sorted output;
  added a `_hhmm()` UI helper.
- `pawpal_system.py` — added the stretch feature `Scheduler.suggest_next_slot()`
  and a shared `_parse_hhmm()` helper (also DRYed `Task.start_minutes()`).
- `diagrams/uml.mmd` (+ `uml_draft.mmd`) — synced classes/relations to final code.
- `README.md` — Features list, Demo Walkthrough, test-coverage summary.
- `reflection.md` — draft answers for the design/testing/reflection sections.

**What did the agent do?**

- Read the real source files before answering rather than guessing, so tests and
  docs referenced actual method names and signatures.
- Ran `pytest` and `python main.py` after changes and reported results (15 tests
  passing; captured genuine CLI output for the README).
- Implemented `suggest_next_slot()`: scans the day as busy `[start, end)` blocks
  and returns the earliest gap that fits a task, with two covering tests.

**What did you have to verify or fix manually?**

- **`git add . / push main`** — I intended to commit the tests, but the agent
  caught that `git add .` from the repo root would have staged a virtualenv and
  embedded the project as a useless gitlink; it committed inside the correct
  sub-repo (on `main`) instead. I confirmed the branch/remote before pushing.
- **Unhashable `Task`** — a first-draft test put tasks in a `set` and raised
  `TypeError` (dataclasses aren't hashable); switched to an ordered-tuple assert.
- **Conflict UX decision** — I kept overlaps as non-fatal *warnings* the owner
  resolves, rather than letting the scheduler auto-drop tasks.
- **Encoding** — cleaned `→`/emoji artifacts (`�`) from the captured CLI output
  before pasting it into the README.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
