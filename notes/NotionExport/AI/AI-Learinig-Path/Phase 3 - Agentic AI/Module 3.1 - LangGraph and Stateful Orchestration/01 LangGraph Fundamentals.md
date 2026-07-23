# 01 — LangGraph Fundamentals: Graphs, State & Edges

> Phase 3 · Module 3.1 · Lesson 1 · `[JD VERIFIED — ~75% of agentic JDs name LangGraph]`

> 🔬 **Currency note (mid-2026):** LangGraph is now **1.x** (`langgraph 1.2.x`) — a stable, production
> framework, not a beta. Everything below uses the current `1.x` API.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** A plain call to an LLM (large language model — the "brain" that turns your text
into more text) is **one-shot and linear**: you send a prompt, you get one reply, the end. But a real
**agent** — an LLM that *does things*: thinks, calls a tool, looks at the result, thinks again — needs
three things a single call can't give you:

1. **Loops** — "think → act → observe → think again" until the job is done (you don't know in advance
   how many times).
2. **Branching** — "if the user asked for data, go to the SQL step; otherwise just answer."
3. **Memory** — each step needs to see what the earlier steps produced.

You *could* hand-code this with a Python `while` loop full of `if/else`. People did, and it became an
unmaintainable mess: no way to pause and resume, no persistence if the process crashed, no streaming,
no way to see *why* the agent did what it did. **LangGraph** is the framework that fixes this: you
describe your agent as a **graph** — a set of **steps (nodes)** connected by **arrows (edges)**, all
sharing one **state** object — and LangGraph runs it for you, with persistence, streaming, and
pause/resume built in.

**Where this sits.** This is the **first** lesson of Phase 3 and the foundation for *everything* after
it: the agent loop (Lesson 02), memory (03), and multi-agent systems (04) are all just bigger graphs.

**Why care (for AI Engineer/Architect roles).** LangGraph is named in ~75% of agentic-AI job posts —
the single most-named agent framework in 2026. It is the tool you will reach for first, and the one
interviewers expect you to reason about.

---

## 🔑 New Terms (plain English)

- **Agent** — an LLM that runs in a loop, deciding for itself which steps/tools to use to reach a goal
  (not just answering once).
- **Graph** — your agent drawn as boxes and arrows: boxes are steps, arrows are the order they run in.
- **Node** — one step in the graph. In code it's just a Python function that does some work.
- **Edge** — an arrow connecting two nodes; it says "after this node, go to that one."
- **State** — a shared data object that travels through the graph; every node reads it and writes
  updates to it. Think of it as the agent's working memory for one run.
- **`StateGraph`** — the LangGraph class you use to build a graph around a state shape.
- **`TypedDict`** — a plain Python dict whose keys/types are declared up front (used to define the
  shape of the State).
- **Reducer** — the *rule* for how a node's update is merged into the state (overwrite the old value,
  or append to it). Set with `Annotated[type, reducer]`.
- **Conditional edge** — a *smart* arrow: a small router function decides which node to go to next.
- **`START` / `END`** — the two built-in markers for "where the graph begins" and "where it stops."
- **Compile** — turn your finished blueprint into a runnable graph (`builder.compile()`).
- **Checkpointer** — a saver that persists state between steps so a run can pause/resume (Lesson 03).
  (All collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: an assembly line with a travelling clipboard)

Picture a factory **assembly line**. A **clipboard** rides along the conveyor belt from station to
station. Each **worker station** picks up the clipboard, reads what's on it, does its bit of work, and
writes its results back onto the *same* clipboard before sending it down the belt. At a **junction**, a
supervisor glances at the clipboard and decides which branch of the line to send it down.

- The **clipboard** is the **State** — the shared data everyone reads and writes.
- Each **station** is a **node** — a function that takes the state and returns an update.
- The **belts** between stations are **edges** — fixed "go here next" arrows.
- The **junction with a supervisor** is a **conditional edge** — a router that picks the next station
  based on what's on the clipboard.

**The "Aha!":** you don't write one giant function with tangled `if/else` and loops. You describe
**small stations** and **how the clipboard flows between them**, and LangGraph runs the line. Because
the whole thing is just "state flowing through a graph," LangGraph can *save the clipboard at every
station* (persistence), *show you each station's work as it happens* (streaming), and *stop the line
for a human to approve something, then resume* (human-in-the-loop) — all for free.

---

## ⚙️ Stage 2 — How It Actually Works

### 2.1 The old painful way (so you feel why the graph exists)

Here's a hand-rolled agent loop — the thing LangGraph replaces:

```python
# ❌ The DIY way: a while-loop agent. Works for a demo, hurts in production.
def run_agent(user_input):
    messages = [{"role": "user", "content": user_input}]
    while True:                                   # loop until done — but how do we KNOW when?
        response = llm.invoke(messages)           # call the model
        messages.append(response)
        if response.tool_calls:                   # branching, by hand
            result = run_tool(response.tool_calls) # act
            messages.append(result)               # observe
            continue                              # ...loop again
        else:
            return response                       # no tool wanted -> we're done
# Problems: no persistence (crash = lose everything), no streaming, no pause/resume,
# no record of WHY each branch was taken, and this gets unreadable fast as steps grow.
```

It runs — but it's a black box you can't pause, persist, stream, or inspect. LangGraph turns this same
idea into an explicit graph you get all those powers for.

### 2.2 The five-step build (a minimal graph, fully commented)

Every LangGraph program follows the same five steps: **define State → write nodes → wire edges →
compile → run.**

```python
from typing import Annotated, TypedDict          # TypedDict = a dict with a declared shape
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages  # a ready-made reducer for chat messages

# --- STEP 1: define the State (the "clipboard" shape) ---------------------------
class State(TypedDict):
    # 'messages' is a list; the add_messages reducer APPENDS new messages
    # instead of overwriting the list (more on reducers in 2.3).
    messages: Annotated[list, add_messages]

# --- STEP 2: write nodes (each is a function: state in -> partial update out) ----
def chatbot(state: State) -> dict:
    # read the running conversation from state, ask the LLM, return an update.
    reply = llm.invoke(state["messages"])     # llm = any chat model you've set up
    return {"messages": [reply]}              # returned dict is MERGED into state

# --- STEP 3: build the graph and wire the edges ---------------------------------
builder = StateGraph(State)                   # create a graph bound to our State shape
builder.add_node("chatbot", chatbot)          # register the node under a name
builder.add_edge(START, "chatbot")            # entry: begin at 'chatbot'
builder.add_edge("chatbot", END)              # exit: after 'chatbot', stop

# --- STEP 4: compile (blueprint -> runnable) ------------------------------------
graph = builder.compile()

# --- STEP 5: run it -------------------------------------------------------------
result = graph.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
print(result["messages"][-1].content)         # the model's reply
```

Read it as a sentence: *"Start → run the `chatbot` node → end,"* with a `messages` list as the shared
clipboard. That's a complete (if tiny) LangGraph app. Everything else is adding more nodes and smarter
edges.

> **Key rule — nodes return *partial* updates, not the whole state.** A node returns only the keys it
> wants to change (`{"messages": [reply]}`), and LangGraph merges that into the full state using each
> key's **reducer**. You never rebuild the whole state by hand.

### 2.3 State & reducers — *how* updates get merged (a real choice)

A **reducer** is the rule for combining a node's returned value with what's already in the state. This
is a genuine decision you make per field, so here is each option as its own mini-reference.

#### Overwrite (the default — no reducer)
- **What & why:** if you declare a field with *no* `Annotated` reducer, a node's update **replaces**
  the old value. Use for fields that hold "the latest value," not a growing history.
- **Key features:** simplest; last write wins; no accumulation.
- **Syntax:**
  ```python
  class State(TypedDict):
      question: str          # plain field -> overwrite
      retry_count: int       # each node sets the new value outright
  ```
- **✅ Use when:** the field is a current snapshot — the active question, a status flag, a counter you
  set to a new number.
- **🚫 Avoid when → use `add_messages`/`operator.add`:** you want to *accumulate* a history (a growing
  message list or a list of results) — overwrite would throw away everything but the last write.
- **⚠️ Gotcha:** if two parallel nodes write the *same* overwrite field in the same step, LangGraph
  can't decide which wins and raises an `InvalidUpdateError` — accumulating fields need a reducer.

#### `add_messages` (the chat-history reducer)
- **What & why:** the purpose-built reducer for a list of chat messages. It **appends** new messages,
  and — cleverly — if an incoming message has the same `id` as an existing one, it **replaces** that
  one (so you can edit/stream a message safely). It also coerces plain dicts to Message objects.
- **Key features:** append-by-default; update-by-id; auto-converts `{"role","content"}` dicts to
  message objects; the backbone of every chat agent.
- **Syntax:**
  ```python
  from langgraph.graph.message import add_messages
  messages: Annotated[list, add_messages]
  # shortcut: `from langgraph.graph import MessagesState` is a prebuilt TypedDict
  # that already contains exactly this `messages` field — subclass it to add more.
  ```
- **✅ Use when:** any conversational agent — basically always, for the `messages` field.
- **🚫 Avoid when → use `operator.add`:** you're accumulating a list of *non-message* things (numbers,
  search hits, custom objects) where the id/Message logic doesn't apply.
- **⚠️ Gotcha:** it keys on message `id`. If you hand-build messages without ids and stream partials,
  you can get duplicates — let the framework/model assign ids.

#### `operator.add` (plain list/number accumulation)
- **What & why:** Python's built-in `+`, used as a reducer to **concatenate lists** (or sum numbers)
  across nodes. The generic "append to a list" when it isn't chat messages.
- **Key features:** dead simple; concatenates lists or adds numbers; great for fan-in/parallel results.
- **Syntax:**
  ```python
  import operator
  search_results: Annotated[list, operator.add]   # each node's list gets concatenated
  ```
- **✅ Use when:** several nodes (often parallel workers, Lesson 04) each contribute items to one
  combined list, or you're summing a value.
- **🚫 Avoid when → use `add_messages`:** the list holds chat messages (you'd lose the id/update logic)
  · **or → write a custom reducer:** you need de-duplication or merging smarter than concatenation.
- **⚠️ Gotcha:** it only *grows*. There's no built-in "cap the list" — long-running graphs can balloon
  the state; trim it yourself or use a custom reducer.

> A **custom reducer** is just a function `(old, new) -> merged` you pass in `Annotated[type, my_fn]` —
> reach for it when you need de-duplication, capping, or merging dicts.

### 2.4 Edges — *how* control flows between nodes (a real choice)

#### Fixed edge — `add_edge`
- **What & why:** an unconditional "after A, always go to B" arrow. The backbone of any straight-line
  flow.
- **Syntax:** `builder.add_edge("A", "B")` · entry/exit use the markers: `add_edge(START, "A")`,
  `add_edge("A", END)`.
- **✅ Use when:** the next step is always the same.
- **🚫 Avoid when → use a conditional edge:** the next step depends on what just happened (e.g. did the
  model ask for a tool?).
- **⚠️ Gotcha:** add an edge into `END` (or a conditional path to `END`), or your graph never stops.

#### Conditional edge — `add_conditional_edges`
- **What & why:** a junction. You give it a **router function** that reads the state and returns the
  **name of the next node** (or `END`). This is what creates **branching** *and* **loops** (route back
  to an earlier node).
- **Key features:** dynamic next-step; enables the ReAct loop (Lesson 02); can return `END` to finish.
- **Syntax:**
  ```python
  def route(state: State) -> str:          # a router: state in -> next node NAME out
      last = state["messages"][-1]
      if last.tool_calls:                  # model asked to use a tool?
          return "tools"                   # -> go to the tools node
      return END                           # -> otherwise we're done

  builder.add_conditional_edges("chatbot", route)
  # optional 3rd arg is a {return_value: node_name} map if your router returns
  # labels rather than node names: add_conditional_edges("chatbot", route,
  #                                                       {"use_tool": "tools", "stop": END})
  ```
- **✅ Use when:** the path forks, or you need to loop until a condition is met.
- **🚫 Avoid when → use a fixed edge:** there's only one possible next step (don't add a router that
  always returns the same thing).
- **⚠️ Gotcha:** the router must return a value that maps to a *real* node name (or `END`). A typo'd
  label that matches nothing raises an error at runtime.

> 🔁 **This is the whole trick behind "agents."** A node that calls the LLM, a conditional edge that
> asks "did it request a tool?", a tools node, and an edge looping *back* to the LLM node — that four-
> piece cycle **is** the ReAct agent loop you'll build in Lesson 02.

### 2.5 Running the graph — `invoke` vs `stream` (a real choice)

#### `invoke` / `ainvoke` — run to completion
- **What & why:** run the whole graph and hand back the **final state**. Simplest.
- **Syntax:** `final = graph.invoke(initial_state)` · async: `await graph.ainvoke(...)`.
- **✅ Use when:** a batch job or a backend call where you only need the end result.
- **🚫 Avoid when → use `stream`:** it's a user-facing chat and you want to show progress/tokens live
  (waiting silently for a long agent run feels broken).
- **⚠️ Gotcha:** for a long multi-step agent, `invoke` returns nothing until the *entire* run finishes.

#### `stream` / `astream` — watch it run, with `stream_mode`
- **What & why:** yield output *as the graph runs*, step by step. The `stream_mode` argument picks
  *what* you get — and this is itself a real choice:

  | `stream_mode=` | You receive | Use it for |
  |---|---|---|
  | `"values"` | the **full state** after each step | simplest progress; show the latest state |
  | `"updates"` | only the **delta each node returned** | logging *which node did what* (most common) |
  | `"messages"` | **LLM tokens** as they're generated | the live "typing…" effect in a chat UI |

- **Syntax:**
  ```python
  for chunk in graph.stream(initial_state, stream_mode="updates"):
      print(chunk)        # -> {'chatbot': {'messages': [...]}} after each node
  ```
- **✅ Use when:** any interactive app — stream `"messages"` for the typing effect, `"updates"` for a
  step log. (You can pass a list of modes to get several at once.)
- **🚫 Avoid when → use `invoke`:** a non-interactive batch job that only needs the final answer.
- **⚠️ Gotcha:** `"messages"` streams *model tokens* and only works if the underlying model supports
  streaming; it's not the same as `"updates"` (node-level), which people often confuse.

> 🔬 **Under the hood.** LangGraph runs on a **Pregel**-style engine (the graph model Google built for
> processing huge graphs). Execution happens in **super-steps**: every "active" node in a step runs
> (potentially in parallel), their returned updates are merged into the state through the **reducers**
> (the state fields are technically *channels*), and then the edges decide which nodes are active for
> the *next* super-step. That's why nodes return partial updates and why parallel writes to a plain
> field are ambiguous — the engine merges all of a step's writes at once. Persistence (Lesson 03) works
> by snapshotting these channels after every super-step.

---

## 🚀 Stage 3 — In Practice / Why It Matters

In real systems you rarely build raw graphs *and* you don't hand-roll the agent loop either — LangGraph
ships a prebuilt agent (`create_react_agent`, Lesson 02) for the common case. But you reach for the raw
`StateGraph` the moment you need **custom control flow**: an approval gate before a risky action,
multiple specialist agents, a reflection/critique loop, or an audit trail of every decision. That
"explicit control flow + state" is exactly why LangGraph dominates production and JD listings: it's the
framework that lets an architect *guarantee* how the agent behaves, instead of hoping a black-box loop
does the right thing.

You'll build directly on these fundamentals: **Lesson 02** turns the `chatbot → route → tools → back`
cycle into a real ReAct agent; **Lesson 03** adds a checkpointer so the State survives across turns and
crashes; **Lesson 04** runs many graphs as supervisor + workers.

---

## ⚖️ Variations & When to Use (the at-a-glance digest)

| Decision | Options | Pick which, when |
|---|---|---|
| **Reducer** (per field) | overwrite · `add_messages` · `operator.add` · custom | snapshot → overwrite · chat history → `add_messages` · accumulate non-messages → `operator.add` · de-dup/cap → custom |
| **Edge** | fixed (`add_edge`) · conditional (`add_conditional_edges`) | always-same-next → fixed · branch or loop → conditional |
| **Run** | `invoke` · `stream` | need only final result → `invoke` · interactive/long → `stream` |
| **`stream_mode`** | `values` · `updates` · `messages` | full state → `values` · per-node log → `updates` · live tokens → `messages` |
| **State base** | `TypedDict` you write · prebuilt `MessagesState` | extra custom fields → your own TypedDict · just chat messages → `MessagesState` |

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| `InvalidUpdateError: At key 'x': Can receive only one value per step` | two nodes wrote the same **overwrite** field in one (parallel) step | give that field a reducer (`operator.add` / custom) so updates merge |
| Graph never stops / recursion limit hit | no path reaches `END`, or a loop has no exit condition | add an edge to `END`; make sure a conditional edge can return `END` |
| `KeyError` on a state field | a node read a key that hasn't been set yet | provide it in the initial input, or give the field a default/reducer |
| Node update ignored | returned the wrong key name, or returned a non-dict | a node must return a `dict` whose keys match State fields |
| Conditional edge crashes | router returned a label with no matching node | return a real node name or `END` (or supply the mapping dict) |
| Messages duplicated when streaming | hand-built messages without ids | let the model/framework assign message ids (works with `add_messages`) |

---

## 📌 Quick Reference (cheat-sheet)

```python
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]   # append + update-by-id
    # plain_field: str                        # overwrite (default)

def node(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}   # partial update

b = StateGraph(State)
b.add_node("chatbot", node)
b.add_edge(START, "chatbot")
b.add_edge("chatbot", END)
graph = b.compile()

graph.invoke({"messages": [{"role": "user", "content": "hi"}]})      # final state
for c in graph.stream(inp, stream_mode="updates"): ...               # step-by-step
```

- **Five steps:** State → nodes → edges → compile → run.
- **Nodes return partial updates**; reducers merge them.
- **Conditional edge = branch/loop**; remember a path to `END`.
- Top gotchas: parallel writes need a reducer · always reach `END` · router must return a real target.

---

## 🛑 STOP — Self-Check

You're building a research agent. It has a `messages` chat list **and** a `sources` list that several
parallel search nodes each add findings to. A teammate declares **both** fields as plain
`TypedDict` entries with no reducer, and the graph crashes with `InvalidUpdateError` the moment two
search nodes run in the same step. **What's wrong, and how do you fix each field?**

<details>
<summary>Answer</summary>

The crash is because **plain fields use the *overwrite* reducer** — "last write wins" — and LangGraph
can't pick a winner when **two parallel nodes write the same field in one super-step**, so it raises
`InvalidUpdateError`. Both fields are accumulating histories, so both need an *appending* reducer:

- **`messages`** → `Annotated[list, add_messages]` — it's chat history, so use the message-aware reducer
  (append + update-by-id).
- **`sources`** → `Annotated[list, operator.add]` — it's a plain list of non-message findings, so plain
  list concatenation is right (or a **custom reducer** if you also need to de-duplicate sources).

The deeper idea: in LangGraph a field's **reducer** *is* its concurrency rule. Anything multiple nodes
contribute to must be declared as accumulating, not overwrite.
</details>

---

⏭️ **Next:** Lesson 02 — **Cyclical Agent Patterns**: turn the `chatbot → route → tools → loop back`
cycle into a real **ReAct** agent (and meet the prebuilt `create_react_agent`).
