# 02 — CrewAI: Role-Based Crews & Event-Driven Flows

> Phase 3 · Module 3.2 · Lesson 2 · `[JD VERIFIED — ~55–65%, named in TCS/Infosys/Accenture JDs]`

> 🔬 **Currency (mid-2026):** CrewAI `1.15.x`. Two paradigms now ship together — **Crews** (autonomous
> role-based teams) and **Flows** (event-driven control). Knowing both is the modern requirement.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** LangGraph gives total control — but you wire every node and edge. For a fast
prototype where you just want *"a researcher and a writer that collaborate,"* that's a lot of ceremony.
**CrewAI** trades some control for speed: describe each agent by its **role, goal, and backstory**, give
them tasks, and they collaborate — a working multi-agent crew in hours. When you later need precise
control, CrewAI adds **Flows** (event-driven steps), so you can mix autonomy with deterministic logic.

**Where this sits.** Lesson 01 said *when* to pick CrewAI; this is the hands-on. It's the second-most-
named framework after LangGraph and a JD staple at Indian IT majors.

**Why care.** You'll be asked to "spin up a CrewAI crew" — and an architect must know Crews **and** Flows
to say *when each*.

---

## 🔑 New Terms (plain English)

- **Agent** — a worker defined by a **role**, **goal**, and **backstory** (its persona drives behaviour).
- **Task** — a unit of work with a description and an expected output, assigned to an agent.
- **Crew** — the team: agents + tasks + a process that runs them.
- **Process** — how tasks run: **sequential** (in order) or **hierarchical** (a manager delegates).
- **`kickoff`** — start the crew with inputs.
- **Flow** — event-driven workflow: deterministic Python steps that trigger each other (and can launch
  crews), with structured state. CrewAI's control-flow answer.
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: a film crew)

A **film crew** is roles: a director, a cinematographer, an editor. You don't micromanage each shutter
press — you cast roles, hand out scenes (tasks), and they collaborate. That's a **Crew**: cast agents by
**role**, assign **tasks**, hit **kickoff**.

A **Flow** is the *shooting schedule*: scene 1 → if weather bad, reshoot → then editing. Deterministic
steps that fire on events — and a scene can itself summon a whole crew.

**The "Aha!":** Crews optimise for **autonomy** (cast + delegate), Flows for **control** (explicit steps).
Combine them: a Flow orchestrates the schedule; Crews do the creative scenes.

---

## ⚙️ Stage 2 — How It Works

### 2.1 A crew (fully commented)

```python
# pip install crewai crewai-tools
from crewai import Agent, Crew, Process, Task

researcher = Agent(
    role="Senior Researcher",                       # WHO it is
    goal="Find the latest facts on {topic}",         # WHAT it optimises for
    backstory="A meticulous analyst known for depth.",# persona that shapes behaviour
    verbose=True,
)
writer = Agent(role="Writer", goal="Write a clear brief on {topic}",
               backstory="A crisp explainer.", verbose=True)

research = Task(description="Research {topic}", expected_output="10 bullet facts", agent=researcher)
report   = Task(description="Write a one-page brief", expected_output="markdown", agent=writer,
                output_file="brief.md")

crew = Crew(agents=[researcher, writer], tasks=[research, report],
            process=Process.sequential, verbose=True)
crew.kickoff(inputs={"topic": "agentic AI"})         # {topic} fills in from inputs
```

Cast roles → assign tasks → kickoff. No graph wiring — that's the speed.

### 2.2 Process: sequential vs hierarchical (a real choice)

#### Sequential
- **What & why:** tasks run top-to-bottom, each feeding the next. Predictable.
- **✅ Use when:** a clear pipeline (research → write → edit). **🚫 Avoid when → hierarchical:** dynamic
  delegation/coordination needed. **⚠️ Gotcha:** order matters — a task can't use a later task's output.

#### Hierarchical
- **What & why:** a **manager** agent delegates and validates. **✅ Use when:** the route depends on
  results. **🚫 Avoid when → sequential:** a fixed pipeline. **⚠️ Gotcha:** the manager adds calls/cost.

### 2.3 Flows for control (a real choice)

```python
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel
class S(BaseModel): score: float = 0.0
class Pipe(Flow[S]):
    @start()
    def analyze(self): return crew.kickoff(...)
    @router(analyze)
    def gate(self): return "high" if self.state.score > 0.8 else "low"
    @listen("high")
    def ship(self): ...
```

- **Crew** — autonomy/roles. **🚫 use Flow when:** need branching/state/audit. **Flow** — control. **🚫 use
  Crew when:** simple collaboration. **⚠️ Gotcha:** Flows are Python steps, not auto-agents — you write logic.

> 🔬 **Under the hood.** A Crew = a prompt loop per role; hierarchical adds a manager LLM. Flows are an
> event engine (`@start/@listen/@router`) over a Pydantic state. CrewAI tools speak **MCP** (`crewai-tools[mcp]`).

---

## 🚀 Stage 3 — In Practice

Demo as a **Crew**; productionise control with **Flows** (or port to LangGraph). YAML config + CLI
(`crewai create crew`) is common; tools via `crewai_tools` or MCP. Architect line: *prototype Crew → keep
in Flows for control or migrate to LangGraph.*

---

## ⚖️ Variations & When to Use

| Decision | Options | Pick |
|---|---|---|
| Process | sequential · hierarchical | pipeline → sequential · dynamic → hierarchical |
| Paradigm | Crew · Flow | autonomy → Crew · control/state → Flow |
| Vs LangGraph | CrewAI · LangGraph | fast roles → CrewAI · fine control → LangGraph |

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Vague output | weak `expected_output` | be specific (format, length) |
| Agent off-track | thin role/backstory | richer role/goal/backstory |
| `{topic}` literal | no input | pass `kickoff(inputs={...})` |
| High cost | hierarchical | use sequential unless delegation needed |

---

## 📌 Quick Reference

```python
Agent(role,goal,backstory,tools); Task(description,expected_output,agent); Crew(agents,tasks,process).kickoff(inputs)
# Flows: Flow[State]; @start/@listen(x)/@router(x)
```
**Crew = roles/autonomy · Flow = control/state · sequential vs hierarchical · MCP for tools.**

---

## 🛑 STOP — Self-Check

A loan workflow: deterministic credit check → if approved, a multi-agent crew writes the offer. Crew, Flow,
or both?

<details><summary>Answer</summary>
**Both.** A **Flow** owns the deterministic check + branch (`@router`); on approval it launches a **Crew**
to draft the offer. Flow = control; Crew = creative collaboration — the combination is CrewAI's strength.
</details>

---

⏭️ **Next:** Lesson 03 — **Semantic Kernel / Microsoft Agent Framework**.
