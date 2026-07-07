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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

My scheduler uses a greedy, priority-first algorithm: it sorts tasks by priority (shortest-duration as a tiebreak) and fills the day until time runs out, without reconsidering earlier choices. The tradeoff is that it optimizes for doing the most important tasks first rather than fitting the most tasks into the day — a long high-priority task can crowd out several shorter ones that would collectively deliver more care. This is reasonable here because a pet owner cares most about the critical tasks (medication, walks) getting done, and because greedy selection stays fast, deterministic, and easy to explain ("scheduled first because it had the highest priority").

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
