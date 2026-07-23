# 04 — Supervisor–Worker Multi-Agent Topologies

> Phase 3 · Module 3.1 · Lesson 4 · `[JD VERIFIED — the dominant production topology]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** You *could* build one giant agent with 20 tools: a SQL tool, a document-search
tool, a web API tool, an email tool… But cram too much into one agent and it gets **worse**: the system
prompt balloons, the model gets confused about *which* of 20 tools to pick, reasoning slows down, and a
mistake in one area poisons the whole run. It's a single employee asked to be lawyer, accountant, and
engineer at once.

The fix mirrors how companies scale: **specialise and delegate.** Build several **specialist agents**,
each focused on one domain (a SQL analyst agent, a document-RAG agent, an API agent), and put a
**supervisor** in front that **routes** each task to the right specialist and collects the results.
That's a **multi-agent system**, and the **supervisor–worker** shape is its most common, most JD-named
form.

**Where this sits.** Lessons 01–03 built and persisted a *single* agent loop. This lesson composes
*many* of those loops into a team. It's the centrepiece of the Module 3.1 milestone (Lesson 06).

**Why care.** "Multi-agent supervisor patterns" sits in ~65% of agentic JDs and is the standard way
real enterprise assistants are architected. Designing the *topology* (who talks to whom) is a core
**architect** skill.

---

## 🔑 New Terms (plain English)

- **Multi-agent system** — several agents that each specialise, working together on a task.
- **Worker (specialist) agent** — an agent focused on one domain (SQL, documents, a specific API).
- **Supervisor** — the coordinator agent that decides which worker handles the next step and merges
  results.
- **Topology** — the *shape* of the team: who can hand off to whom (hub-and-spoke, peer-to-peer, etc.).
- **Routing** — choosing which agent/node runs next based on the task.
- **Handoff** — one agent passing control (and context) to another.
- **`Command`** — a LangGraph object a node returns to **update state *and* route in one move**
  (`Command(goto="sql_agent", update={...})`). The modern handoff mechanism.
- **`Send`** — dispatch the *same* node many times in parallel, each with different input — the **fan-
  out** (map) primitive.
- **Fan-out / map-reduce** — split work into parallel pieces (map), then combine the results (reduce).
- **Aggregation node** — the node that merges parallel workers' outputs into one result (the reduce).
- **Subgraph** — a whole compiled graph used *as a node* inside a bigger graph (each worker is often a
  subgraph). (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: a manager and their team)

A good **manager** doesn't personally do the SQL, write the report, *and* call the API. They **triage**:
read the incoming request, decide "this is a data question — send it to the **analyst**," wait for the
result, maybe then route to the **writer**, and finally hand the polished result back to the customer.
Each **specialist** is excellent at their *one* thing and ignores the rest.

That's the **supervisor–worker** topology. The **supervisor** is the manager (pure routing + merging);
the **workers** are the specialists (each its own agent from Lessons 01–03). The supervisor never does
the specialist work itself — it **delegates** and **aggregates**.

**The "Aha!":** a multi-agent system is just a **graph whose nodes are themselves agents**. The
supervisor is a node that, instead of calling a *tool*, decides which *agent* runs next. Everything you
learned about nodes, edges, and state still applies — the "tools" just got promoted to "teammates."

---

## ⚙️ Stage 2 — How It Actually Works

### 2.1 The supervisor loop (hub-and-spoke)

```
                 ┌──────────────────────────────────────────┐
                 ▼                                           │
 START → [ SUPERVISOR ] ──route──► [ sql_agent ] ───────────┤
                 │      ──route──► [ doc_agent ] ────────────┤  (each worker
                 │      ──route──► [ api_agent ] ────────────┘   returns to
                 └────────────────► END  (when work is done)     the supervisor)
```

The supervisor decides who's next; each worker does its bit and reports **back** to the supervisor; the
supervisor loops until the task is complete, then routes to `END`.

### 2.2 Building it with `Command` (the modern handoff)

The key tool is **`Command`**: a node returns it to *both* write to the state **and** say where to go
next — routing without a separate conditional edge.

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.types import Command

# --- the SUPERVISOR: reads the task, picks the next worker (or finishes) -------
def supervisor(state: MessagesState) -> Command[Literal["sql_agent", "doc_agent", "__end__"]]:
    decision = router_llm.invoke(state["messages"])   # an LLM (or rules) picks the next worker
    next_node = decision["next"]                       # e.g. "sql_agent" | "doc_agent" | "FINISH"
    if next_node == "FINISH":
        return Command(goto=END)
    # route to the chosen worker AND record the decision in state, in one step:
    return Command(goto=next_node, update={"messages": [decision["message"]]})

# --- a WORKER: does its specialist job, then hands control BACK to supervisor --
def sql_agent(state: MessagesState) -> Command[Literal["supervisor"]]:
    result = sql_subagent.invoke(state)                # a full agent (Lessons 01-03) as a subgraph
    return Command(goto="supervisor", update={"messages": result["messages"]})

builder = StateGraph(MessagesState)
builder.add_node("supervisor", supervisor)
builder.add_node("sql_agent", sql_agent)
builder.add_node("doc_agent", doc_agent)
builder.add_edge(START, "supervisor")
graph = builder.compile()
# Note: no manual edges between supervisor and workers - Command(goto=...) routes dynamically.
```

`Command(goto=..., update=...)` is the whole handoff: **update** carries the context forward, **goto**
transfers control. The `Literal[...]` return hint tells LangGraph the legal destinations so it can draw
and validate the graph.

### 2.3 The prebuilt shortcut

You don't have to hand-wire supervisors either — there are prebuilt packages:

```python
from langgraph_supervisor import create_supervisor   # pip install langgraph-supervisor

app = create_supervisor(
    agents=[sql_agent, doc_agent, api_agent],         # your worker agents
    model=llm,
    prompt="You are a supervisor. Route each request to the right specialist.",
).compile(checkpointer=checkpointer)
# (langgraph-swarm offers the peer-to-peer 'swarm' topology instead.)
```

Use the prebuilt for the standard shape; hand-build with `Command` when you need custom routing logic.

### 2.4 Parallel fan-out with `Send` (map-reduce)

Sometimes you don't want to route to *one* worker — you want to run the **same** step over **many**
items at once (analyse 50 documents, call 5 APIs). That's **`Send`**: the map (fan-out) primitive.

```python
from langgraph.types import Send

# MAP: dispatch one "analyze" run per document, in parallel, each with its own input.
def fan_out(state) -> list[Send]:
    return [Send("analyze", {"doc": d}) for d in state["documents"]]

builder.add_conditional_edges("dispatch", fan_out, ["analyze"])
# Each parallel "analyze" appends to a results list via an operator.add reducer (Lesson 01)...
# REDUCE: a later "aggregate" node reads the combined results and merges them into one answer.
```

The parallel results land in a list field whose **reducer** (`operator.add`, Lesson 01) concatenates
them — that's why accumulating fields need a reducer. An **aggregation node** then reduces them to the
final output.

### 2.5 The topology choices (each as a mini-reference)

#### Supervisor (hub-and-spoke)
- **What & why:** one coordinator routes to workers; workers report back to it. Central control + a
  clean audit trail of every routing decision.
- **Key features:** simple to reason about; easy to log/govern; the default.
- **✅ Use when:** distinct specialists and you want one place that owns orchestration (most enterprise
  assistants).
- **🚫 Avoid when → use a swarm/network:** agents need to hand off *directly* to each other frequently
  and routing everything through one hub is a bottleneck.
- **⚠️ Gotcha:** the supervisor is a single point of failure and a token cost on every hop — keep its
  prompt tight and its routing cheap.

#### Network / Swarm (peer-to-peer)
- **What & why:** any agent can hand off to any other directly (no central hub). Flexible, emergent
  collaboration.
- **Key features:** direct handoffs; no bottleneck; `langgraph-swarm` prebuilt.
- **✅ Use when:** agents genuinely collaborate as peers and the next agent depends on context only the
  *current* agent has.
- **🚫 Avoid when → use a supervisor:** you need central control, predictable routing, or strong
  auditability (peer handoffs are harder to govern and can loop).
- **⚠️ Gotcha:** without a coordinator, agents can ping-pong handoffs — add loop limits and clear
  handoff rules.

#### Hierarchical (supervisor of supervisors)
- **What & why:** teams of workers, each team under a mid-level supervisor, all under a top supervisor.
  Scales to many agents by adding layers.
- **Key features:** nested subgraphs; divides a big org into manageable teams.
- **✅ Use when:** the system is large enough that one flat supervisor over *all* workers gets unwieldy.
- **🚫 Avoid when → use a flat supervisor:** you only have a handful of workers (layers add latency and
  complexity you don't need).
- **⚠️ Gotcha:** every layer adds an LLM hop — more latency and cost; only add depth you actually need.

#### Parallel / Map-Reduce (`Send` fan-out)
- **What & why:** run the *same* operation over many inputs simultaneously, then aggregate. Throughput,
  not routing.
- **Key features:** `Send` map step + accumulating reducer + aggregate node; big speed-ups on batchable
  work.
- **✅ Use when:** independent, parallelisable subtasks (score N documents, query M sources).
- **🚫 Avoid when → use sequential routing:** the steps depend on each other's results (you can't
  parallelise a chain).
- **⚠️ Gotcha:** the accumulator field **must** have a reducer (`operator.add`) or parallel writes raise
  `InvalidUpdateError` (Lesson 01); also watch rate limits when fanning out wide.

> 🔬 **Under the hood.** Each worker is typically its own **compiled graph used as a node** (a
> *subgraph*) — so a "multi-agent system" is graphs nested inside a graph, sharing (or mapping between)
> state. `Command(goto=X)` simply sets node `X` as the active node for the next super-step, which is why
> it can route *and* update in one return. `Send(node, payload)` schedules extra parallel invocations of
> a node for the next super-step — the same Pregel engine from Lesson 01, just fanning out.

---

## 🚀 Stage 3 — In Practice / Why It Matters

The textbook enterprise assistant — and the Module 3.1 milestone — is a **supervisor** routing to a
**SQL analyst agent**, a **document-RAG agent** (your Phase 2 work!), and an **external-API agent**, all
**persisted** with a Postgres checkpointer (Lesson 03). That single design answers a huge range of
business questions because each worker is independently strong and the supervisor composes them.

As an architect, your real value here is **choosing the topology**: a flat supervisor for a handful of
specialists, hierarchical when it grows, `Send` fan-out for batch work, and a swarm only when peer
handoffs truly beat central routing. Getting that shape right — and keeping the supervisor cheap and
auditable — is what separates a robust multi-agent system from an expensive, looping mess.

---

## ⚖️ Variations & When to Use (the at-a-glance digest)

| Topology | Shape | Pick it when |
|---|---|---|
| **Supervisor** | hub-and-spoke (1 coordinator) | distinct specialists + central control (the default) |
| **Network / Swarm** | peer-to-peer handoffs | agents collaborate directly; hub would bottleneck |
| **Hierarchical** | supervisors of supervisors | many agents; one flat supervisor is unwieldy |
| **Parallel / Map-Reduce** | `Send` fan-out + aggregate | many independent, batchable subtasks |

> Mechanism cheat: **`Command(goto, update)`** = route + update in one (handoff) · **`Send`** = parallel
> fan-out · **prebuilt** `create_supervisor` / `langgraph-swarm` for the standard shapes.

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| `InvalidUpdateError` during fan-out | parallel `Send` workers write a field with no reducer | give the accumulator field `operator.add` (or custom) |
| Supervisor & workers loop forever | no `FINISH`/`END` route, or workers don't report back correctly | give the supervisor an `END` path; workers `Command(goto="supervisor")` |
| `Command goto` target invalid | routed to a node name that doesn't exist | match a real node name (or `END`); declare destinations in the `Literal[...]` hint |
| Workers don't see needed context | `update` didn't carry the context forward | include the needed messages/fields in `Command(update=...)` |
| Parallel fan-out hammers an API | fanning out wider than rate limits allow | batch/limit concurrency; add backoff in the worker |
| One worker's error kills everything | no error handling in the worker subgraph | add error-recovery (Lesson 02) inside each worker |

---

## 📌 Quick Reference (cheat-sheet)

```python
from typing import Literal
from langgraph.types import Command, Send
from langgraph.graph import StateGraph, START, END, MessagesState

# Supervisor routes via Command(goto, update); workers hand back to "supervisor".
def supervisor(state) -> Command[Literal["worker_a", "worker_b", "__end__"]]:
    nxt = pick_next(state)
    return Command(goto=END) if nxt == "FINISH" else Command(goto=nxt, update={...})

# Parallel fan-out (map) then aggregate (reduce):
def fan_out(state) -> list[Send]:
    return [Send("analyze", {"item": x}) for x in state["items"]]

# Prebuilt:
from langgraph_supervisor import create_supervisor
app = create_supervisor(agents=[a, b], model=llm, prompt="route...").compile()
```

- **Multi-agent = a graph whose nodes are agents.** Supervisor routes; workers specialise + report back.
- **`Command(goto, update)`** = handoff (route + state) in one return.
- **`Send`** = parallel fan-out; the accumulator needs a reducer.
- Topology: supervisor (default) · swarm (peer) · hierarchical (scale) · map-reduce (batch).

---

## 🛑 STOP — Self-Check

You design a "research team": a supervisor routes a question to a **web-search agent** and a **SQL
agent**, then to a **writer agent**. You also want to summarise **30 source documents at once** before
writing. Which mechanism handles the **routing between the three agents**, and which handles the
**30-documents-at-once** step — and what one piece of State configuration does the second require?

<details>
<summary>Answer</summary>

- **Routing between the three agents** → the **supervisor pattern using `Command(goto=..., update=...)`**
  (a hub-and-spoke topology). The supervisor reads the task and hands off to web-search, SQL, or writer,
  each returning control to the supervisor — sequential, central, auditable routing.

- **Summarising 30 documents at once** → **`Send` (parallel fan-out / map-reduce)**: dispatch 30 parallel
  `summarize` runs, one per document, then an **aggregation node** reduces them into one combined summary
  for the writer.

- **The required State config:** the field the 30 parallel runs write into **must have an accumulating
  reducer** — `Annotated[list, operator.add]` (Lesson 01). Without it, the simultaneous writes collide
  and LangGraph raises `InvalidUpdateError`, because a plain (overwrite) field can't accept multiple
  values in one super-step.

So: `Command` for **routing** (one specialist at a time), `Send` + a reducer for **parallel throughput**
(many identical tasks at once) — two different tools for two different jobs.
</details>

---

⏭️ **Next:** Lesson 05 — **Advanced LangGraph Patterns**: subgraphs, dynamic graph construction,
streaming intermediate results, and the LangGraph Platform for deployment.
