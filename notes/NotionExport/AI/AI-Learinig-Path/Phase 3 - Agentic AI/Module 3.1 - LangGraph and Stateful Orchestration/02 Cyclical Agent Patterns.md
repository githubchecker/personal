# 02 — Cyclical Agent Patterns: ReAct, Tools, Reflection

> Phase 3 · Module 3.1 · Lesson 2 · `[JD VERIFIED — the core "agent loop"]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** In Lesson 01 you built a graph that calls the model once and stops. But an
**agent** has to *do* things it can't do in one shot: look something up, run a calculation, query a
database, then **use that result to decide its next move**. A single straight-line graph can't do
"think → act → look at the result → think again" — that needs a **cycle** (a loop in the graph).

This lesson is about the **shape of that loop**. The famous one is **ReAct** (Reason + Act), and almost
every agent you'll build or read about is a variation of it. Once you can draw the ReAct cycle as a
graph, you understand 90% of agent design.

**Where this sits.** Lesson 01 gave you nodes/edges/state. This lesson wires them into the **agent
loop** — the beating heart of Phase 3. Lessons 03–04 then make that loop *stateful* and *multi-agent*.

**Why care.** "Build a ReAct/tool-calling agent" is the single most common agentic interview task and
JD requirement. It's also the thing candidates most often get *fuzzy* about — knowing the exact four-
piece cycle sets you apart.

---

## 🔑 New Terms (plain English)

- **Tool** — a function the LLM is allowed to call (search the web, run SQL, do math). You define it;
  the model decides *when* to use it. (Full lesson: Module 3.3.)
- **Tool call** — the model's structured request "please run tool `X` with these arguments." It's not
  the model running code — it's the model *asking your program* to.
- **Observation** — the result your program gets back from running the tool, fed to the model so it can
  react.
- **ReAct (Reason + Act)** — the loop: the model **reasons**, optionally **acts** (calls a tool), sees
  the **observation**, and reasons again — until it has the answer.
- **`bind_tools`** — attaches your tools to the model so it *knows they exist* and can emit tool calls.
- **`ToolNode`** — a prebuilt LangGraph node that runs whatever tools the model asked for and returns
  the results as messages.
- **`tools_condition`** — a prebuilt router that checks "did the model ask for a tool?" and routes to
  the tools node or to `END`.
- **`create_react_agent`** — a one-line prebuilt that builds the whole ReAct graph for you.
- **Reflection** — a pattern where the agent **critiques its own output** and revises it.
- **Plan-and-execute** — a pattern that **plans all the steps first**, then executes them.
  (Collected in the [AI Terms glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md).)

---

## 🎈 Stage 1 — The Simple Idea (analogy: a detective working a case)

A detective doesn't solve a case in one thought. They **think** ("the timeline doesn't add up"), then
**act** on a clue (check an alibi, run a fingerprint), then **look at what came back** (the observation),
then **think again** with the new fact. They repeat this loop until the case is closed — and crucially,
*they* decide each time whether they need another clue or they're ready to name the culprit.

That's **ReAct**. The LLM is the detective. **Reasoning** is its thinking. A **tool call** is checking a
clue. The **observation** is what the clue reveals. And the loop continues until the model decides it
has enough to answer — at which point it stops asking for tools and just replies.

**The "Aha!":** the agent loop isn't magic — it's a **cycle in the graph**: an LLM node, a "did it ask
for a tool?" junction, a tools node, and an arrow looping *back* to the LLM node. The model itself
chooses when to exit the loop (by not requesting a tool).

---

## ⚙️ Stage 2 — How It Actually Works

### 2.1 The ReAct cycle as a graph (four pieces)

```
            ┌─────────── loop back with the observation ───────────┐
            ▼                                                       │
  START → [ agent: LLM(+tools) ] —— tools_condition ——► [ tools: ToolNode ]
                                          │
                                          └──(no tool wanted)──► END
```

Four pieces, and you already know three of them from Lesson 01:
1. an **agent node** (the LLM, with tools bound),
2. a **conditional edge** (`tools_condition`: "did it ask for a tool?"),
3. a **tools node** (`ToolNode`: runs the requested tools),
4. a **fixed edge looping back** from tools → agent.

### 2.2 Building it by hand (fully commented)

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

# 1) Define tools (just Python functions; full detail in Module 3.3).
def get_weather(city: str) -> str:
    """Get the current weather for a city."""        # the docstring tells the LLM what it does
    return f"It's 22°C and sunny in {city}."

tools = [get_weather]

# 2) Bind the tools to the model so it KNOWS they exist and can request them.
llm_with_tools = llm.bind_tools(tools)

# 3) The agent node: call the tool-aware model on the running conversation.
def agent(state: MessagesState) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# 4) Wire the cycle. (MessagesState is the prebuilt State from Lesson 01:
#    a single `messages` field with the add_messages reducer.)
builder = StateGraph(MessagesState)
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))      # prebuilt: runs requested tools
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)  # -> "tools" or END
builder.add_edge("tools", "agent")              # THE LOOP: observation goes back to the model
graph = builder.compile()

graph.invoke({"messages": [{"role": "user", "content": "What's the weather in Paris?"}]})
# Flow: agent asks for get_weather("Paris") -> tools runs it -> observation back to agent
#       -> agent now has the fact -> no tool needed -> END with the final answer.
```

That `add_edge("tools", "agent")` is the entire difference between a one-shot chain and an **agent**:
the result of acting flows *back* into reasoning.

### 2.3 The prebuilt shortcut — `create_react_agent`

You won't hand-wire that cycle every time. LangGraph ships it as a one-liner — use it for the common
case, and drop to the manual graph only when you need custom control flow.

```python
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(llm, tools)          # builds the whole ReAct graph above
agent.invoke({"messages": [{"role": "user", "content": "Weather in Paris?"}]})

# Common options:
# create_react_agent(llm, tools,
#                    prompt="You are a concise weather assistant.",   # system prompt
#                    checkpointer=checkpointer)                       # memory (Lesson 03)
```

> 🔬 **Under the hood — what a "tool call" really is.** When you `bind_tools`, the framework sends the
> model a JSON description of each tool (name, what it does, its parameters — auto-generated from your
> function's signature and docstring; Module 3.3). The model doesn't run anything; it **emits structured
> JSON** like `{"name": "get_weather", "args": {"city": "Paris"}}`. `ToolNode` reads that, runs the real
> Python function, and appends the result as a **`ToolMessage`** with the matching `tool_call_id`. The
> model sees that message on the next loop and reasons over it. So "the model used a tool" is really
> *the model asked, your code ran it, the answer was fed back* — a strict request/response handshake.

### 2.4 The four agent patterns (each as a mini-reference)

ReAct is the default, but several loop *shapes* exist. Each is a real design choice, so here's the
when/why for each.

#### ReAct (Reason + Act) — the default loop
- **What & why:** interleave reasoning and tool use; the model decides each step whether to act or
  answer. The general-purpose agent.
- **Key features:** flexible; handles open-ended tasks; minimal structure; the prebuilt
  `create_react_agent`.
- **✅ Use when:** general tool-using assistants, Q&A-with-lookup, "do whatever it takes" tasks of
  small-to-medium length.
- **🚫 Avoid when → use plan-and-execute:** the task has many steps that benefit from a plan up front
  (ReAct can wander or lose the thread on long tasks).
- **⚠️ Gotcha:** with no step cap it can loop too long or repeat a failing tool — set a recursion limit
  and good tool descriptions.

#### Reflection (self-critique → revise)
- **What & why:** the agent produces a draft, a **critic step** judges it against criteria, and the
  agent **revises** — looped until "good enough." Trades extra calls for quality.
- **Key features:** a generator node + a critic node + a loop; big quality lift on writing, code, and
  reasoning tasks.
- **✅ Use when:** output quality matters more than latency/cost — essays, code, structured analysis.
- **🚫 Avoid when → use plain ReAct:** simple lookups or latency-sensitive paths (reflection multiplies
  token cost and time).
- **⚠️ Gotcha:** needs a **stop rule** (max iterations or a "no further improvements" check) or it
  critiques forever.

#### Plan-and-Execute (plan first, then do)
- **What & why:** a **planner** writes the full list of steps up front; an **executor** runs them one by
  one (re-planning if reality diverges). Separates "what to do" from "doing it."
- **Key features:** explicit plan (auditable); steadier on long multi-step jobs; often cheaper (the big
  model plans once; a smaller model executes).
- **✅ Use when:** long, multi-step tasks where a visible plan helps (research, multi-stage workflows).
- **🚫 Avoid when → use ReAct:** short tasks where planning overhead isn't worth it.
- **⚠️ Gotcha:** a rigid plan can go stale if a step fails — allow **re-planning** when an executor step
  returns something unexpected.

#### Error-recovery / retry loop
- **What & why:** wrap tool calls so a **failure** routes to a retry/handle node instead of crashing the
  graph — retry, try a fallback, or escalate to a human (Module 3.5).
- **Key features:** a conditional edge on tool success/failure; retry-with-backoff; escalation paths.
- **✅ Use when:** production agents touching flaky tools/APIs (always, basically, for real systems).
- **🚫 Avoid when → keep it simple:** a throwaway prototype where a crash is acceptable.
- **⚠️ Gotcha:** cap the retries — an unconditional retry loop on a permanently-broken tool spins
  forever and burns tokens.

---

## 🚀 Stage 3 — In Practice / Why It Matters

Most production agents are **ReAct + error-recovery**, with **reflection** added where quality is
critical and **plan-and-execute** for long workflows. You'll almost always *start* from
`create_react_agent` and only drop to the hand-built graph when you need to insert a custom node — a
human-approval gate (Module 3.5), a guardrail check, or a specific routing rule. That ability to take
the prebuilt loop and *open it up* is precisely the architect skill LangGraph is prized for.

These patterns also compose: a **supervisor** (Lesson 04) is often a ReAct agent whose "tools" are
*other agents*; a reflection loop can live *inside* one worker. Master the single loop here and the
multi-agent systems later are just loops-of-loops.

---

## ⚖️ Variations & When to Use (the at-a-glance digest)

| Pattern | One-line shape | Pick it when |
|---|---|---|
| **ReAct** | reason ⇄ act, model decides when to stop | general tool-using tasks (the default) |
| **Reflection** | draft → critique → revise (loop) | quality > cost: writing, code, analysis |
| **Plan-and-Execute** | plan all steps → run each | long multi-step jobs needing a visible plan |
| **Error-recovery** | tool fails → retry / fallback / escalate | any production agent touching real APIs |

> Build vs prebuilt: **`create_react_agent`** for the standard loop; **hand-built `StateGraph`** the
> moment you need a custom node (approval gate, guardrail, bespoke routing).

---

## 🐛 Common Errors & Fixes

| Symptom | Cause | Fix |
|---|---|---|
| `GraphRecursionError: Recursion limit reached` | the loop never exits (model keeps calling tools, or a tool always fails) | improve tool descriptions; cap with `config={"recursion_limit": N}`; add an exit/escalation path |
| Model never calls the tool | tools not bound, or weak docstring/description | use `llm.bind_tools(tools)`; write a clear docstring saying *when* to use it |
| `ToolMessage` missing / mismatched `tool_call_id` | hand-built the tools step instead of `ToolNode` | use the prebuilt `ToolNode`, which sets ids correctly |
| Tool runs but model ignores the result | observation not fed back | ensure the `tools → agent` loop edge exists so the result returns to the model |
| Agent loops re-calling the same failing tool | no error handling | add an error-recovery branch and a retry cap |

---

## 📌 Quick Reference (cheat-sheet)

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition, create_react_agent

# --- Prebuilt (use first) ---
agent = create_react_agent(llm, tools, prompt="...", checkpointer=cp)

# --- Manual ReAct cycle (when you need custom nodes) ---
b = StateGraph(MessagesState)
b.add_node("agent", lambda s: {"messages": [llm.bind_tools(tools).invoke(s["messages"])]})
b.add_node("tools", ToolNode(tools))
b.add_edge(START, "agent")
b.add_conditional_edges("agent", tools_condition)   # -> "tools" or END
b.add_edge("tools", "agent")                        # the loop
graph = b.compile()
```

- **The loop = agent → (tool? ) → tools → back to agent.** The back-edge is what makes it an agent.
- A **tool call** is structured JSON the model emits; your code runs it; the result returns as a
  `ToolMessage`.
- Patterns: **ReAct** (default) · **Reflection** (quality) · **Plan-execute** (long tasks) ·
  **Error-recovery** (production).
- Always cap iterations (`recursion_limit`) and write strong tool descriptions.

---

## 🛑 STOP — Self-Check

In the hand-built ReAct graph, you have `add_conditional_edges("agent", tools_condition)` and
`add_edge("tools", "agent")`. A colleague "simplifies" it by replacing the conditional edge with a
plain `add_edge("agent", "tools")`. **What breaks, and why?**

<details>
<summary>Answer</summary>

The agent **can never finish**. `tools_condition` is the exit door: it checks whether the model's last
message contains a tool call — if **yes**, route to `tools`; if **no**, route to **`END`**. Replacing it
with a fixed `add_edge("agent", "tools")` means *after every* agent step you go to the tools node
unconditionally — even when the model produced a final answer and asked for **no** tool. The tools node
then has nothing valid to run (or errors), loops back to the agent, and you spin until the recursion
limit throws `GraphRecursionError`.

The lesson: in a ReAct loop the **conditional edge is the stop condition**. The model signals "I'm done"
by *not* requesting a tool, and only `tools_condition` (or an equivalent router) can detect that and
route to `END`.
</details>

---

⏭️ **Next:** Lesson 03 — **Memory & Persistence**: add a **checkpointer** so the State survives across
turns (and crashes), giving your agent real short- and long-term memory.
