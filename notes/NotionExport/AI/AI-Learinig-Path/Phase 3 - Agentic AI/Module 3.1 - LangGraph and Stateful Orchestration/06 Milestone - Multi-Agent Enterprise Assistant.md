# 06 — 🏁 Milestone: Multi-Agent Enterprise Assistant

> Phase 3 · Module 3.1 · Lesson 6 · `[MILESTONE — portfolio centrepiece]`

> This milestone ties together **all of Module 3.1**. It's a *project brief*, not a new concept — build
> it to prove you can design and ship a stateful, supervised, multi-agent system. This is the kind of
> project that anchors a Lead/Architect portfolio.

---

## 🎯 The goal

Build an **enterprise assistant** where a **supervisor** routes each request to the right specialist
**worker agent**, and the whole system is **stateful** (persisted with PostgreSQL). One assistant that
can answer data questions, document questions, and act on external systems — by delegating.

**Three workers, one supervisor:**
- **SQL Analyst agent** — turns natural-language questions into SQL against a business database and
  explains the result.
- **Document-RAG agent** — your Phase 2 retrieval pipeline as an agent (answers from the document store).
- **External-API agent** — calls an outside service (e.g. a weather/CRM/ticketing API) on request.

```
                     ┌──────────── loop until done ───────────┐
                     ▼                                         │
 user ─► START ─► [ SUPERVISOR ] ─route─► [ SQL Analyst ]──────┤
                     │          ─route─► [ Document-RAG ]──────┤
                     │          ─route─► [ External-API ]──────┘
                     └──────────────────► END ─► final answer
        (all State persisted in PostgreSQL via a checkpointer; one thread per conversation)
```

---

## 🧱 Build steps (each maps to a lesson)

1. **State + graph skeleton** *(Lesson 01)* — define a `MessagesState`-based State; create the
   `StateGraph`; wire `START → supervisor`.
2. **Build each worker as an agent** *(Lessons 02 + 05)* — each specialist is its own
   `create_react_agent` (or hand-built ReAct graph) with its own tools, composed as a **subgraph**.
   - SQL agent → a SQL tool (Module 3.3); Document agent → your Phase 2 retriever as a tool;
     API agent → an authenticated REST tool.
3. **Supervisor routing** *(Lesson 04)* — a supervisor node returning `Command(goto=worker, update=…)`;
   workers hand back with `Command(goto="supervisor")`; supervisor routes to `END` when done. (Or use
   the prebuilt `create_supervisor`.)
4. **Persistence** *(Lesson 03)* — compile with a **`PostgresSaver`**; pass `thread_id` per
   conversation; confirm a follow-up question remembers the previous turn.
5. **Streaming** *(Lessons 01 + 05)* — stream the run so the user sees which specialist is working
   (`stream_mode="updates"` or `astream_events`).
6. **(Optional) error recovery** *(Lesson 02)* — wrap worker tools so a failure retries or reports
   gracefully instead of crashing the graph.

---

## ✅ Acceptance criteria (definition of done)

- [ ] A single entry point answers a question by **routing to the correct worker** (verify all three
      fire on appropriate questions).
- [ ] A **multi-step** question uses **more than one** worker in a single run (e.g. "look up X in the
      docs, then check its live status via the API").
- [ ] **Memory works:** a follow-up referring to the previous turn ("and for *that* customer…") is
      answered correctly using the **same `thread_id`**.
- [ ] State **survives a restart** (PostgreSQL checkpointer, not `MemorySaver`).
- [ ] The run **streams** intermediate progress (not a silent 20-second wait).
- [ ] A wrong/failed tool call **doesn't crash** the whole assistant.

---

## 🚀 Stretch goals (portfolio polish)

- **Human-in-the-loop gate** *(Module 3.5)* — pause for approval before the API agent performs a
  write/action.
- **Parallel fan-out** *(Lesson 04)* — have the document agent summarise many sources at once with
  `Send`.
- **Hierarchical teams** *(Lesson 05)* — group workers under sub-supervisors as the system grows.
- **Observability** *(Phase 4)* — wire **LangSmith** tracing to inspect every routing decision.
- **Deploy** *(Lesson 05)* — run it on the **LangGraph Platform** (or self-hosted server) with the
  Assistants API.

---

## 🧠 What this proves

Finishing this means you can do the thing ~75% of agentic JDs ask for: **design a stateful, multi-agent
LangGraph system** — choosing the topology, persisting state correctly, composing specialist agents, and
making it production-shaped. That's the core Phase 3 competency, demonstrated end-to-end.

---

⏭️ **Next:** Module 3.2 — **The 2026 Agent Framework Landscape**: when LangGraph is the right call, and
when CrewAI, Semantic Kernel / Microsoft Agent Framework, or the OpenAI Agents SDK fits better.
