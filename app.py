from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler


def _hhmm(minutes: int) -> str:
    """Format minutes-since-midnight back into an 'HH:MM' clock string."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Persist the Owner in the session "vault" so data survives reruns. -----
# On first load, restore from data.json if it exists; otherwise start fresh.
if "owner" not in st.session_state:
    st.session_state.owner = (
        Owner.load_from_json() or Owner(name="Jordan", available_minutes_per_day=60)
    )

owner = st.session_state.owner

# Save the full owner graph (pets + tasks) to data.json between runs.
if st.button("💾 Save data"):
    owner.save_to_json()
    st.success("Saved to data.json — your pets and tasks will be here next run.")

# --- Owner settings --------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes_per_day = st.number_input(
    "Time available per day (minutes)", min_value=0, max_value=1440,
    value=owner.available_minutes_per_day,
)

st.divider()

# --- Add a Pet -------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed", value="")
    age = st.number_input("Age", min_value=0, max_value=50, value=1)
    if st.form_submit_button("Add pet"):
        # Owner.add_pet() handles the data; the rerun re-renders the list below.
        owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
        st.success(f"Added {pet_name}.")

if not owner.pets:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task (attached to one of the owner's pets) -----------------
st.subheader("Schedule a Task")
if owner.pets:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("For which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        category = st.text_input("Category", value="walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["daily", "weekly"])
        set_time = st.checkbox("Set a start time (enables sorting + conflict checks)")
        start_time = st.time_input("Start time", value=time(8, 0), disabled=not set_time)
        if st.form_submit_button("Add task"):
            pet = next(p for p in owner.pets if p.name == pet_choice)
            # Pet.add_task() attaches the task (and stamps the pet's name).
            pet.add_task(
                Task(
                    name=task_title,
                    category=category,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    # "HH:MM" is what Scheduler.sort_by_time / find_conflicts expect.
                    due_time=start_time.strftime("%H:%M") if set_time else None,
                )
            )
            st.success(f"Added '{task_title}' for {pet_choice}.")
else:
    st.caption("Add a pet first, then you can schedule tasks for it.")

# --- Show each pet and its tasks (renders from the persisted owner) --------
for pet in owner.pets:
    with st.expander(f"🐾 {pet.name} ({pet.species}) — {len(pet.tasks)} task(s)", expanded=True):
        if pet.tasks:
            st.table(
                [
                    {
                        "task": t.name,
                        "time": t.due_time or "—",
                        "minutes": t.duration_minutes,
                        "priority": t.priority,
                        "frequency": t.frequency,
                        "done": t.completed,
                    }
                    for t in pet.tasks
                ]
            )
        else:
            st.caption("No tasks yet.")

st.divider()

# --- Build Schedule --------------------------------------------------------
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not owner.all_tasks():
        st.warning("No tasks to schedule yet. Add a pet and some tasks first.")
    else:
        # Owner.view_daily_schedule() builds a Scheduler and returns a DailyPlan.
        plan = owner.view_daily_schedule()
        # A Scheduler over the same tasks gives us sorting + conflict checks.
        scheduler = Scheduler.from_owner(owner)

        st.markdown(f"### Today's Schedule for {owner.name}")
        st.caption(plan.summary())

        # Scheduler.find_conflicts(): timed tasks whose [start, end) windows overlap.
        conflicts = scheduler.find_conflicts(plan.scheduled)
        if conflicts:
            st.warning(
                f"⚠️ {len(conflicts)} scheduling conflict(s) — you can't be in two "
                "places at once. Consider moving or shortening one task in each row."
            )
            st.table(
                [
                    {
                        "overlap": f"{_hhmm(max(a.start_minutes(), b.start_minutes()))}"
                        f"–{_hhmm(min(a.end_minutes(), b.end_minutes()))}",
                        "task A": f"{a.name} ({a.pet_name or '?'}) {a.due_time}",
                        "task B": f"{b.name} ({b.pet_name or '?'}) {b.due_time}",
                    }
                    for a, b in conflicts
                ]
            )
        else:
            st.success("✅ No time conflicts — the day flows cleanly.")

        if plan.scheduled:
            st.markdown("**Scheduled** (ordered by start time)")
            # Scheduler.sort_by_time(): earliest due_time first, untimed last.
            st.table(
                [
                    {"time": t.due_time or "—", "task": t.name, "pet": t.pet_name,
                     "minutes": t.duration_minutes, "priority": t.priority}
                    for t in scheduler.sort_by_time(plan.scheduled)
                ]
            )
        if plan.skipped:
            st.markdown("**Skipped (no time left)**")
            st.table(
                [
                    {"task": t.name, "pet": t.pet_name, "minutes": t.duration_minutes}
                    for t in plan.skipped
                ]
            )

        with st.expander("Why these decisions?"):
            for line in plan.explanations:
                st.write("•", line)
