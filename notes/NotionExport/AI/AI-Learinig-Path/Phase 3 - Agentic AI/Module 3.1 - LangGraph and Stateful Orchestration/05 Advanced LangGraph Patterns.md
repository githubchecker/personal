# 05 — Advanced LangGraph Patterns

> Phase 3 · Module 3.1 · Lesson 5 · `[ARCHITECT BONUS — 🟡 SHOULD, lighter than the MUST lessons]`

> ⚠️ **Scope.** These are the patterns that turn a working agent into a *production, architect-grade*
> system. You don't need them for your first agent, but interviewers for Lead/Architect roles expect you
> to **know they exist and when to reach for each**. Treat this as solid awareness with enough hands-on
> to speak credibly.

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** Lessons 01–04 build one capable, persisted, multi-agent system. But shipping it
raises four new questions:
1. **Reuse** — my "document agent" is used in three places; how do I avoid copy-pasting its graph? →
   **subgraphs**.
2. **Flexibility** — different customers enable different features; how do I build the graph *per
   request* instead of hard-coding it? → **dynamic graph construction**.
3. **UX on long runs** — a 30-second agent run feels broken if the UI just spins; how do I show
   progress live? → **streaming intermediate results**.
4. **Deployment** — how do I run this as a scalable service with scheduling and webhooks, not a script?
   → **LangGraph Platform**.

**Where this sits.** The capstone of Module 3.1: the polish layer over the fundamentals. None of it is
new *theory* — it's composition and operations built on the same graph/state model.

**Why care.** These are the answers to "how would you take this agent to production?" — the exact
architect-level question that decides senior interviews.

---

## 🔑 New Terms (plain English)

- **Subgraph** — a complete compiled graph used *as a single node* inside a bigger graph (composition).
- **Dynamic graph construction** — assembling the graph at **runtime** from config, instead of writing
  it out statically.
- **`astream_events`** — a streaming API that emits fine-grained events (model tokens, tool starts/ends,
  node steps) so a frontend can show live progress.
- **LangGraph Platform** — LangChain's managed deployment for LangGraph apps: a server, persistence,
  cron scheduling, webhooks, and an Assistants API.
- **Assistant** — a deployed, configured instance of your graph (a graph + its settings) on the Platform.
- **Cron schedule** — "run this graph automatically on a timetable" (e.g. a daily report agent).
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: from a recipe to a restaurant)

Lessons 01–04 wrote a great **recipe**. This lesson is about running a **restaurant**:

- A **subgraph** is a *sub-recipe* (your house sauce) you reuse in many dishes instead of rewriting it.
- **Dynamic construction** is assembling the night's **menu** from whatever's in stock today, rather
  than one fixed menu forever.
- **Streaming intermediate results** is the waiter telling you "starters are plated, mains in five" —
  progress, so you're not staring at an empty table.
- The **LangGraph Platform** is the *building, staff, and booking system* — everything that turns a
  recipe into a service that runs reliably at scale.

**The "Aha!":** nothing here changes the cooking (the graph). It's all **composition and operations** —
reuse sub-recipes, build menus on the fly, narrate progress, and run it as a real service.

---

## ⚙️ Stage 2 — How It Actually Works

### 2.1 Subgraphs — graphs as nodes (a real choice: how to connect their state)

A subgraph is just a compiled graph added as a node. The only real decision is whether parent and child
**share the same State shape** or not.

#### Shared state schema (drop it in directly)
- **What & why:** parent and subgraph share state keys, so you add the compiled subgraph *as a node*
  directly. Simplest composition.
- **Syntax:**
  ```python
  subgraph = sub_builder.compile()
  parent.add_node("doc_agent", subgraph)   # the compiled subgraph IS the node
  ```
- **✅ Use when:** the subgraph naturally operates on the same `messages`/state as the parent (most
  same-team workers).
- **🚫 Avoid when → use the wrapper style:** the subgraph has a *different* state shape (different keys).
- **⚠️ Gotcha:** shared keys mean shared reducers — the child's writes merge into the parent under the
  parent's rules; make sure that's what you want.

#### Different state schema (wrap with a transform)
- **What & why:** the subgraph has its *own* state shape, so you wrap it in a function that **maps
  parent state → child input** and **child output → parent update**.
- **Syntax:**
  ```python
  def call_doc_agent(state: ParentState) -> dict:
      result = subgraph.invoke({"query": state["messages"][-1].content})  # map IN
      return {"messages": [result["answer"]]}                              # map OUT
  parent.add_node("doc_agent", call_doc_agent)
  ```
- **✅ Use when:** the subgraph is a reusable component with its own internal state you don't want to
  leak into the parent.
- **🚫 Avoid when → use shared schema:** the shapes already match (the wrapper is needless boilerplate).
- **⚠️ Gotcha:** you own the translation — forget to map a needed field and the subgraph silently runs
  on missing input.

> Subgraphs are how the multi-agent workers in Lesson 04 are *actually* built: each specialist is a
> compiled graph, composed into the supervisor's graph.

### 2.2 Dynamic graph construction (build from config at runtime)

Instead of hard-coding nodes, **assemble** the graph from config — enable a web-search node only if the
tenant has it, add a compliance node only in regulated regions, etc.

```python
def build_graph(config: dict):
    b = StateGraph(State)
    b.add_node("agent", agent)
    if config["tools"]["web_search"]:      # only wire nodes the config turns on
        b.add_node("search", search_node)
        b.add_edge("search", "agent")
    if config["compliance_required"]:
        b.add_node("compliance", compliance_gate)
    b.add_edge(START, "agent")
    return b.compile(checkpointer=cp)
```

- **✅ Use when:** multi-tenant apps, feature flags, or per-user capability sets.
- **⚠️ Gotcha:** more runtime paths = more to test. Validate the assembled graph (every path reaches
  `END`) and log *which* configuration produced it.

### 2.3 Streaming intermediate results to a frontend

Lesson 01 covered `stream_mode`. For rich UIs, **`astream_events`** emits granular events — model
tokens, tool starts/ends, node transitions — so you can render "🔍 searching… ✅ found 3 docs… ✍️
writing…" live during a long run.

```python
async for event in graph.astream_events(inp, version="v2"):
    kind = event["event"]
    if kind == "on_chat_model_stream":     # an LLM token
        yield event["data"]["chunk"].content
    elif kind == "on_tool_start":          # a tool began
        yield f"\n🔧 using {event['name']}…"
    elif kind == "on_tool_end":            # a tool returned
        yield "✅ done"
```

- **✅ Use when:** user-facing agents whose runs take more than a second or two (which is most of them).
- **🚫 Avoid when → use simple `stream(stream_mode=...)`:** you only need node-level updates, not
  token/tool granularity (`astream_events` is richer but more to handle).
- **⚠️ Gotcha:** there are *many* event types — filter to the few your UI needs, and pin the `version`.

### 2.4 LangGraph Platform (deployment)

Locally you run `langgraph dev`. To ship, the **LangGraph Platform** (or self-hosted server) gives you a
production runtime without building one:

- **Managed server + persistence** — your graph behind an API, with checkpointing wired in.
- **Assistants API** — deploy a graph as configurable **assistants** (same graph, different settings).
- **Cron scheduling** — run a graph on a timetable (a nightly summary agent).
- **Webhooks** — trigger a run from an external event; get notified when a long run finishes.
- **Streaming + double-texting handling** — built-in support for long runs and mid-run user messages.

```jsonc
// langgraph.json — the deployment manifest
{
  "graphs": { "assistant": "./agent.py:graph" },
  "dependencies": ["."],
  "env": ".env"
}
```

- **✅ Use when:** you need a scalable, scheduled, observable service (it pairs with LangSmith for
  tracing — Phase 4).
- **🚫 Avoid when → just run the server yourself:** a simple internal tool where managed hosting/cron
  aren't worth it; you can self-host the open server.
- **⚠️ Gotcha:** it's an *operational* layer, not magic — you still design the graph; the Platform runs
  and scales it.

> 🔬 **Under the hood.** A subgraph compiles to the same Pregel engine and is invoked as a node — nesting
> is "graphs all the way down." `astream_events` taps the callback stream every component already emits
> (model, tool, chain) and tags each with a node path. The Platform is essentially a hardened server that
> hosts your compiled graph, owns the checkpointer/Store, and adds scheduling, webhooks, and the
> Assistants API around it.

---

## 🚀 Stage 3 — In Practice / Why It Matters

In production you'll use **subgraphs** to keep each agent reusable, **`astream_events`** to make long
runs feel responsive, and either the **LangGraph Platform** or a self-hosted LangGraph server to deploy —
almost always paired with **LangSmith** for observability (Phase 4). **Dynamic construction** shows up in
multi-tenant SaaS where each customer gets a slightly different agent. As an architect, naming these four
moves — *reuse, build-per-request, stream, deploy* — is how you answer "take this to production" with
specifics instead of hand-waving.

---

## ⚖️ Variations & When to Use (the at-a-glance digest)

| Need | Reach for | Note |
|---|---|---|
| Reuse a graph in many places | **Subgraph** | shared schema → drop in; different schema → wrap with transform |
| Build the graph from config | **Dynamic construction** | multi-tenant / feature flags; test every path |
| Live progress in the UI | **`astream_events`** | richer than `stream_mode`; filter event types |
| Node-level progress only | **`stream(stream_mode=...)`** (Lesson 01) | simpler when you don't need tokens/tools |
| Run as a scalable service | **LangGraph Platform** / self-host | cron, webhooks, Assistants API, + LangSmith |

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Subgraph runs on missing data | different-schema subgraph, mapping omitted a field | map *all* needed fields IN (and back OUT) in the wrapper |
| Subgraph writes clobber parent state | shared-schema subgraph shares a reducer you didn't intend | use a wrapper + separate schema, or align reducers deliberately |
| `astream_events` floods the UI | rendering every event type | filter to the handful you need; pin `version="v2"` |
| Dynamic graph has a dead path | a config branch never reaches `END` | validate the assembled graph; test each config combination |
| Deploy fails to find the graph | wrong path in `langgraph.json` | point `graphs` at `module.py:variable` of the **compiled** graph |

---

## 📌 Quick Reference (cheat-sheet)

```python
# Subgraph (shared schema): drop the compiled graph in as a node
parent.add_node("worker", sub_builder.compile())

# Subgraph (different schema): wrap with an in/out transform
def call(state): return {"messages": [subgraph.invoke({"q": ...})["answer"]]}

# Live progress
async for e in graph.astream_events(inp, version="v2"):
    ...  # on_chat_model_stream | on_tool_start | on_tool_end

# Deploy: langgraph.json -> {"graphs": {"assistant": "./agent.py:graph"}}; `langgraph dev` locally
```

- **Subgraph** = graph as a node (reuse); shared-schema → direct, different-schema → wrap.
- **Dynamic construction** = build from config (multi-tenant); test every path.
- **`astream_events`** = granular live progress; **`stream_mode`** = simpler node updates.
- **LangGraph Platform** = managed server + cron + webhooks + Assistants API (deploy layer).

---

## 🛑 STOP — Self-Check

You have a reusable **document-RAG agent** with its *own* internal state (`{"query", "chunks",
"answer"}`) and you want to plug it into a supervisor whose state is just `{"messages"}`. Which subgraph
integration style do you use, and what specific responsibility falls on *you*?

<details>
<summary>Answer</summary>

Use the **different-state-schema (wrapper) style**. Because the subgraph's state shape (`query/chunks/
answer`) doesn't match the parent's (`messages`), you **wrap** it in a node function that does the
**translation both ways**: map parent → child on the way in (e.g. `query = state["messages"][-1].content`)
and child → parent on the way out (e.g. return `{"messages": [result["answer"]]}`).

The responsibility that falls on you: **the in/out mapping is yours to get right.** If you forget to pass
a field the subgraph needs, it runs on missing input silently; if you forget to map the result back, the
parent never sees the answer. (The shared-schema "drop it in directly" style only works when the shapes
already match — which they don't here.)
</details>

---

⏭️ **Next:** Lesson 06 — 🏁 **Milestone: Multi-Agent Enterprise Assistant** — combine everything in
Module 3.1 into one stateful, supervised, multi-agent system.
