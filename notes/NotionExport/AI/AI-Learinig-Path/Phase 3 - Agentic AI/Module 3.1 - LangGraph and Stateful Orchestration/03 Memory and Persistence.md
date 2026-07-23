# 03 — Memory & Persistence: Checkpointers & Threads

> Phase 3 · Module 3.1 · Lesson 3 · `[JD VERIFIED — what makes an agent *stateful*]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** The graphs in Lessons 01–02 have **amnesia**. Call `graph.invoke(...)`, get an
answer, and the moment it returns, *everything is forgotten*. Ask a follow-up — "and what about
tomorrow?" — and the agent has no idea what "tomorrow" refers to, because the previous turn's State is
gone. Worse: if the process crashes mid-run, the whole conversation is lost.

Real assistants need to **remember**:
- **Short-term** — the current conversation, so turn 5 can see turns 1–4.
- **Long-term** — facts about the user that persist *across separate sessions* ("you told me last week
  you're vegetarian").

LangGraph gives you both through one mechanism: **persistence**. Add a **checkpointer** and the graph
**saves its State after every step**, tied to a conversation id (**thread_id**). That single change is
what turns a stateless chain into a **stateful agent** — and unlocks crash-recovery, human-in-the-loop,
and "time travel" debugging as bonuses.

**Where this sits.** Lessons 01–02 built the loop. This lesson makes it *remember*. Lesson 04 (multi-
agent) and Module 3.5 (human-in-the-loop) both depend on the persistence you set up here.

**Why care.** "PostgreSQL/Redis checkpointing" appears in ~60% of agentic JDs as a *mandatory* skill —
because a demo agent that forgets everything is useless in production. Persistence is the line between
toy and product.

---

## 🔑 New Terms (plain English)

- **Persistence** — saving the agent's State so it survives between calls and crashes.
- **Checkpointer** — the component that does the saving: it snapshots State after every step.
- **Checkpoint** — one saved snapshot of the State at a point in time.
- **Thread** — one conversation/session. Identified by a **`thread_id`**.
- **`thread_id`** — the key that says *which* conversation this call belongs to. Same id = continue;
  new id = fresh start.
- **Short-term memory** — the State of the current thread (the running conversation).
- **Long-term memory** — facts kept *across* threads/sessions, in a **Store**.
- **Store** — a key-value box for long-term memory, namespaced (usually per user).
- **`MemorySaver`** — the in-RAM checkpointer for development.
- **`PostgresSaver` / `RedisSaver`** — production checkpointers backed by a real database.
- **Durable execution** — because every step is saved, a crashed run can **resume from the last
  checkpoint** instead of restarting.
- **Time travel** — replaying or branching from an *earlier* checkpoint (great for debugging).
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: the notepad and the filing cabinet)

You're a support agent taking phone calls.

- During **one call**, you scribble on a **notepad** — names, what they asked, what you've tried so far.
  That's **short-term memory**: the State of *this* conversation (this **thread**). When the call ends,
  you tear off the page.
- But you also keep a **filing cabinet** of **client folders**. Before tearing off the page, you file
  the important bits ("prefers email, account #4471") into that client's folder. Next week, when the
  same client calls, you pull their folder and already know them. That's **long-term memory**: the
  **Store**, kept *across* calls.

And the magic part: imagine the notepad **auto-saves a photocopy after every sentence you write**. If
the call drops, you grab the last photocopy and resume *exactly* where you were — nothing lost. That
auto-save is the **checkpointer**, and the **`thread_id`** is the client's phone number written at the
top of the page so you always grab the *right* notepad.

**The "Aha!":** memory isn't a feature you code into each node — it's **persistence of the State**.
Snapshot the State per conversation (checkpointer + thread_id) and the agent *automatically* remembers,
resumes, and can even rewind.

---

## ⚙️ Stage 2 — How It Actually Works

### 2.1 Short-term memory: a checkpointer + a thread_id (the whole trick)

Two changes to a Lesson-02 graph give it memory:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()                       # 1) an auto-save (in RAM, for dev)
graph = builder.compile(checkpointer=checkpointer) # attach it at compile time

# 2) every call names its conversation via thread_id:
config = {"configurable": {"thread_id": "user-123"}}

graph.invoke({"messages": [{"role": "user", "content": "Hi, I'm Sam."}]}, config)
graph.invoke({"messages": [{"role": "user", "content": "What's my name?"}]}, config)
# -> "Your name is Sam."  The 2nd call sees the 1st because they share thread_id "user-123".

graph.invoke({"messages": [{"role": "user", "content": "What's my name?"}]},
             {"configurable": {"thread_id": "someone-else"}})
# -> "I don't know your name."  Different thread_id = a separate, empty conversation.
```

That's it. You don't append history by hand — the checkpointer reloads the thread's saved State before
each call and saves the updated State after. **`thread_id` is the conversation key.**

### 2.2 Inspecting and rewinding (what persistence unlocks)

Because every step is saved, you can read and even rewind the State:

```python
snapshot = graph.get_state(config)            # the current saved State for this thread
history  = list(graph.get_state_history(config))  # every past checkpoint (newest first)
# Pass an older checkpoint's config back into invoke/stream to "time travel" -
# replay or branch the run from that point. Invaluable for debugging agents.
```

This is also the foundation of **human-in-the-loop** (Module 3.5): the graph can **pause** at a
checkpoint, wait for a human, and **resume** — only possible because the State is durably saved.

### 2.3 The checkpointer choices (each as a mini-reference)

The *interface* is identical; you swap the backend to match the environment. Genuine choice → mini-refs.

#### `MemorySaver` (in-RAM)
- **What & why:** stores checkpoints in process memory. Zero setup. For development and tests.
- **Key features:** instant; no DB; **lost when the process exits**.
- **Syntax:** `from langgraph.checkpoint.memory import MemorySaver; cp = MemorySaver()`.
- **✅ Use when:** local dev, notebooks, unit tests, quick demos.
- **🚫 Avoid when → use `PostgresSaver`/`RedisSaver`:** anything that must survive a restart or run
  across multiple server processes (i.e. production).
- **⚠️ Gotcha:** it's volatile — a restart wipes all conversations. Never ship it as your prod store.

#### `SqliteSaver` (single-file DB)
- **What & why:** persists to a local SQLite file — survives restarts without running a server.
- **Key features:** durable; file-based; single-machine.
- **Syntax:** `from langgraph.checkpoint.sqlite import SqliteSaver` (async: `.aio AsyncSqliteSaver`).
- **✅ Use when:** a single-process app, a desktop tool, or a small prototype that must remember across
  restarts.
- **🚫 Avoid when → use `PostgresSaver`:** multiple server instances or high concurrency (SQLite locks
  on concurrent writes and doesn't share across machines).
- **⚠️ Gotcha:** not built for many concurrent writers — fine for one process, not a web fleet.

#### `PostgresSaver` (production default)
- **What & why:** stores checkpoints in PostgreSQL — durable, concurrent, shared across all your server
  instances. The standard production choice (and the one JDs name).
- **Key features:** durable; multi-process/multi-node; transactional; sync **and** async variants.
- **Syntax:**
  ```python
  from langgraph.checkpoint.postgres import PostgresSaver
  with PostgresSaver.from_conn_string("postgresql://...") as cp:
      cp.setup()                                  # first run: create the tables
      graph = builder.compile(checkpointer=cp)
  # async: from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
  ```
- **✅ Use when:** production web apps, anything horizontally scaled, anything needing durable audit of
  state. If you already run Postgres (e.g. pgvector from Phase 2), reuse it.
- **🚫 Avoid when → use `RedisSaver`:** you specifically want very low-latency/ephemeral session state
  and already run Redis · **or → `MemorySaver`:** local dev.
- **⚠️ Gotcha:** call `.setup()` once to create tables, and use the **async** saver in an async app — a
  sync saver in an async server can block the event loop.

#### `RedisSaver` (low-latency / ephemeral)
- **What & why:** checkpoints in Redis — extremely fast, ideal where sessions are short-lived and you
  already run Redis.
- **Key features:** very low latency; easy TTL/expiry on sessions; needs a Redis server.
- **Syntax:** `from langgraph.checkpoint.redis import RedisSaver` (package `langgraph-checkpoint-redis`).
- **✅ Use when:** high-throughput chat with short sessions; you want sessions to auto-expire.
- **🚫 Avoid when → use `PostgresSaver`:** you need long-term durable/queryable history and strong
  persistence guarantees (Redis is memory-first).
- **⚠️ Gotcha:** if Redis is configured as a cache with eviction, checkpoints can be evicted — configure
  persistence/no-eviction for data you must keep.

### 2.4 Long-term memory: the Store (across sessions)

A checkpointer remembers *one thread*. To remember a user **across** threads/sessions, add a **Store** —
a namespaced key-value box for facts.

```python
from langgraph.store.memory import InMemoryStore       # prod: PostgresStore / RedisStore
store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)

# Inside a node, save and recall facts namespaced by user:
def remember(state, *, store):
    ns = ("memories", "user-123")                      # namespace = (category, user)
    store.put(ns, "diet", {"text": "vegetarian"})      # save a fact
    hits = store.search(ns, query="food preferences")  # recall facts (semantic if configured)
    return {...}
```

- **Checkpointer** = short-term, *per thread* (this conversation).
- **Store** = long-term, *per user across threads* (everything you know about them).
Use **both**: the checkpointer for the live conversation, the Store for durable user knowledge.

> 🔬 **Under the hood.** After each **super-step** (Lesson 01), LangGraph serializes the graph's channel
> values into a **checkpoint** and writes it keyed by `(thread_id, checkpoint_id)`, with a pointer to the
> parent checkpoint — so the history is a linked chain you can walk backwards (time travel) or branch.
> On the next call it loads the latest checkpoint for that `thread_id`, runs the new input on top, and
> saves again. "Memory" is literally *load-latest-snapshot → run → save-new-snapshot*, every turn.

---

## 🚀 Stage 3 — In Practice / Why It Matters

A production agent almost always compiles with a **`PostgresSaver`** (or `RedisSaver`) checkpointer and,
if it personalises, a **Store** for long-term facts. The `thread_id` is wired to *your* identifiers —
typically one thread per user-conversation (`f"{user_id}:{conversation_id}"`). This is also what makes
agents **resumable**: a long research agent that dies at step 12 of 20 can resume from checkpoint 12
instead of redoing everything — the "durable execution" LangGraph is built around.

Crucially, persistence is the **prerequisite for human-in-the-loop** (Module 3.5): you can only *pause
for human approval and resume later* because the State is safely checkpointed in between. So this lesson
quietly unlocks the governance patterns that make agents safe for real enterprise use.

---

## ⚖️ Variations & When to Use (the at-a-glance digest)

| Need | Use |
|---|---|
| Local dev / tests | **`MemorySaver`** (in-RAM, volatile) |
| Single-process app that survives restarts | **`SqliteSaver`** (one file) |
| **Production, scaled web app** | **`PostgresSaver`** (durable, multi-node) — the default |
| High-throughput, short-lived sessions | **`RedisSaver`** (fast, TTL-friendly) |
| Remember a user **across** sessions | add a **Store** (long-term memory) |

| Concept | Scope | Lives in |
|---|---|---|
| **Checkpointer** | one thread (conversation) | short-term State snapshots |
| **Store** | across threads (per user) | long-term facts |

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| Agent forgets the previous turn | no checkpointer, or a *different* `thread_id` each call | compile with a checkpointer **and** reuse the same `thread_id` |
| `ValueError: Checkpointer requires ... thread_id` | invoked a checkpointed graph without `config` | pass `config={"configurable": {"thread_id": "..."}}` |
| Memory lost on restart | using `MemorySaver` in production | switch to `PostgresSaver`/`RedisSaver` |
| `relation "checkpoints" does not exist` (Postgres) | tables not created | call `checkpointer.setup()` once |
| Event loop blocked / slow under load | sync saver in an async server | use `AsyncPostgresSaver` / `AsyncRedisSaver` |
| Cross-session facts not recalled | expecting the checkpointer to do long-term memory | add a **Store**; checkpointer is per-thread only |

---

## 📌 Quick Reference (cheat-sheet)

```python
# Short-term memory: checkpointer + thread_id
from langgraph.checkpoint.memory import MemorySaver         # dev
# from langgraph.checkpoint.postgres import PostgresSaver   # prod
graph = builder.compile(checkpointer=MemorySaver())
cfg = {"configurable": {"thread_id": "user-123"}}
graph.invoke(inp, cfg)                 # same thread_id continues the conversation

graph.get_state(cfg)                   # current snapshot
graph.get_state_history(cfg)           # all checkpoints (time travel)

# Long-term memory: a Store (across sessions)
from langgraph.store.memory import InMemoryStore
graph = builder.compile(checkpointer=cp, store=InMemoryStore())
```

- **Memory = persistence of State.** Checkpointer saves it; `thread_id` says which conversation.
- **Checkpointer = short-term (per thread); Store = long-term (per user).**
- Dev → `MemorySaver`; **prod → `PostgresSaver`** (or `RedisSaver`); call `.setup()` for Postgres.
- Same `thread_id` continues; new `thread_id` starts fresh. Use async savers in async apps.

---

## 🛑 STOP — Self-Check

A teammate's agent "remembers" fine in their notebook with `MemorySaver`, but in production users report
it **forgets everything after each message** — *and* a returning user's preferences from last week are
also gone. Name the **two distinct** problems and the fix for each.

<details>
<summary>Answer</summary>

**Problem 1 — short-term memory isn't persisting in production.** `MemorySaver` keeps checkpoints in
**process RAM**. In production (multiple server instances, and processes that restart/scale), a follow-up
request often hits a *different* process that has none of the in-RAM state — so the conversation looks
empty every time. **Fix:** compile with a **durable, shared checkpointer** — `PostgresSaver` (or
`RedisSaver`) — so all instances read/write the same saved State (and remember to reuse the same
`thread_id` per conversation).

**Problem 2 — there's no long-term memory at all.** A checkpointer only remembers **within one thread**.
Last week's session was a *different* thread, so a checkpointer — even a durable one — won't recall it.
**Fix:** add a **Store** (e.g. `PostgresStore`) and have the agent write durable user facts into it,
namespaced by user, then read them back at the start of new sessions.

The key distinction: **checkpointer = short-term, per conversation; Store = long-term, per user across
conversations.** Production needs the checkpointer to be *durable* **and** a Store for cross-session
memory.
</details>

---

⏭️ **Next:** Lesson 04 — **Supervisor–Worker Multi-Agent Topologies**: one supervisor routing work to
specialist agents, with parallel fan-out (`Send`) and result aggregation.
