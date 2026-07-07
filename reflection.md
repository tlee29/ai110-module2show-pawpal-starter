# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
>> Owner own pet objects 
>> Each pet has multiple task objects
>> Scheduler uses the Owner and Task information to create a DailyPlan
>> Streamlit UI communicates with these classes 
- What classes did you include, and what responsibilities did you assign to each?
>> Owner: name, available time per day, and scheduling preference
>> Pet: name, species, age, care tasks
>> Task: pet care tasks: task name, duration, priority, frequency, and completion status
>> Scheduler: scheduling algorithm: selects and orders tasks based on available time, task priority, and owner preferences to generate the daily care plan

**b. Design changes**

- Did your design change during implementation?
>> Yes
- If yes, describe at least one change and why you made it.
>> explain_decisions() can't works as a standalone method/ fixed to return both the ordered tasks and the explanations together and drop the separate method

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
>>My scheduler weighs three constraints. (1) Time budget — the owner has a fixed number of available minutes per day (available_minutes_per_day), and fits_time_budget() is the hard limit: a task is only scheduled if it fits in the minutes left. (2) Priority — every task carries a low/medium/high label that priority_score() turns into a number (1/2/3), which decides scheduling order. (3) Owner preferences — if a task's name or category matches a stated preference (e.g. "medication"), priority_score() adds a bonus, so a preferred task can outrank one that's nominally higher priority. A fourth, softer constraint is recurrence/due-date: is_due_today() filters out tasks that aren't actually due before any of this even runs, so weekly tasks don't get considered every day.
- How did you decide which constraints mattered most?
>>I treated time as a hard constraint and priority as the ranking rule, because they answer two different questions: priority decides what I'd ideally do first, and time decides what actually fits. Time had to be non-negotiable — a pet owner literally can't spend minutes they don't have — so it's enforced as a strict cutoff rather than something the algorithm can trade away. Priority came next because the whole point of the app is making sure the important care (meds, walks) happens even on a busy day. Preferences I deliberately made the weakest lever — a +2 bonus that can nudge ordering but not override the priority tiers wholesale — because they're a personalization nicety, not a care requirement. I left conflict detection out of the scheduling decision on purpose: overlapping times are surfaced as warnings (conflict_warnings()) rather than used to auto-drop tasks, so the owner stays in control of resolving clashes.

**b. Tradeoffs**

>>My scheduler uses a greedy, priority-first algorithm: it sorts tasks by priority (shortest-duration as a tiebreak) and fills the day until time runs out, without reconsidering earlier choices. The tradeoff is that it optimizes for doing the most important tasks first rather than fitting the most tasks into the day — a long high-priority task can crowd out several shorter ones that would collectively deliver more care. This is reasonable here because a pet owner cares most about the critical tasks (medication, walks) getting done, and because greedy selection stays fast, deterministic, and easy to explain ("scheduled first because it had the highest priority").

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
>> built from the scratch to the end(testing)
- What kinds of prompts or questions were most helpful?
>> "if it notices any missing relationships or potential logic bottlenecks."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
>> when AI built logics that connects dots between UMLs
- How did you evaluate or verify what the AI suggested?
>> by proofreading

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
>>I tested sorting by time, task filtering, daily/weekly recurrence (including auto-spawning the next occurrence), and conflict detection — including the boundary case where back-to-back tasks touch but don't overlap.
- Why were these tests important?
>>These are the paths where a subtle bug produces a silently wrong plan instead of a crash, so they protect the behaviors a pet owner actually relies on.

**b. Confidence**

- How confident are you that your scheduler works correctly?
>>Fairly
- What edge cases would you test next if you had more time?
>>An end-to-end generate_schedule test where a task's duration exactly equals the remaining budget, plus the preference-bonus case where a matched medium task should outrank a plain high one.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
>>folding the scheduled/skipped tasks and the per-task explanations into a single object computed in one pass, so the app can always show why it made each decision.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
>>I'd make conflict detection feed back into scheduling (or at least suggest a resolution) instead of only warning, and add an end-to-end test for the full greedy generate_schedule flow.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
>>I learned that a clean class design pays off most when requirements shift — like dropping the standalone explain_decisions() method and moving explanations into DailyPlan — and that AI is most useful when I verify its suggestions against real behavior rather than accepting them as-is.

## 6. Summarization
>> It was an impressive experience to build the logic layer, implement algorithmic intelligence, and develop tests from beginning to end in collaboration with AI.