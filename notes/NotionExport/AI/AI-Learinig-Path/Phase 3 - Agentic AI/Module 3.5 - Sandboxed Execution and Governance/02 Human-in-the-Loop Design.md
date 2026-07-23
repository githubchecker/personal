# 02 — Human-in-the-Loop (HITL) Design

> Phase 3 · Module 3.5 · Lesson 2 · `[JD VERIFIED — MUST; approval gates for risky agent actions]`

---

## 🗺️ Stage 0 — Concept Map

**The problem first.** A fully autonomous agent that can spend money, email customers, or delete records
is a liability. Before risky actions you want a **human to approve**. **Human-in-the-loop (HITL)** pauses
the graph, surfaces the proposed action, waits for a human, then resumes — possible *only* because state
is checkpointed (Lesson 3.1.03). This is what makes agents safe for finance, GDPR, and real enterprise use.

**Why care:** mandatory in regulated agentic JDs; the difference between a demo and a deployable system.

## 🔑 New Terms
- **HITL** — pause for human approval mid-run. **`interrupt()`** — LangGraph call that suspends the graph.
  **`Command(resume=…)`** — resume with the human's decision. **Escalation trigger** — rule deciding *when*
  to ask (dollar threshold, sensitive op, low confidence). **Audit log** — record of every decision.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: a junior employee books travel freely but needs a manager's sign-off above £1,000. The agent pauses, the human approves/edits/rejects, then work resumes. **Aha!:** pause+resume is just a saved checkpoint waiting on a human.

## ⚙️ Stage 2 — How It Works
The whole thing rests on the checkpointer from Lesson 3.1.03: because state is saved, the graph can stop and
continue later. `interrupt()` pauses and surfaces a payload to the human; resuming with a `Command` injects
their decision back in.
```python
from langgraph.types import interrupt, Command
def approve(state):
    decision = interrupt({"action": state["proposed"], "cost": state["amount"]})  # PAUSE, show human
    return {"approved": decision}                       # continues here after human responds
# later, when the human clicks Approve:
graph.invoke(Command(resume=True), config)              # RESUME (needs checkpointer + thread_id)
```

### The patterns (mini-references)
#### interrupt → resume
- **What & why:** suspend the run for sign-off, then continue exactly where it stopped. **✅ Use when:** any
  risky action. **🚫 Avoid → autonomous:** trivial, reversible steps. **⚠️ Gotcha:** no checkpointer = can't resume.
#### Escalation triggers — gate only what matters
- **What & why:** a rule decides *when* to ask a human: cost over a threshold, sensitive op, or low model
  confidence. **✅:** money/sensitive/uncertain. **🚫 Avoid:** gating everything (alert fatigue → rubber-stamping). **⚠️:** tune thresholds.
#### Async approval — for slow humans
- **What & why:** agent suspends; a webhook resumes it when the human responds hours later. **✅:** real ops. **⚠️:** durable checkpointer.
#### Audit logging — record every decision (compliance: GDPR, finance).

> 🔬 `interrupt` saves a checkpoint and stops; resume reloads it and feeds the decision in — pure Lesson-03 persistence.

## 🚀 Stage 3 — In Practice / Why It Matters
HITL is what makes an agent **deployable** in finance, healthcare, or anything GDPR-touched: the agent works
autonomously until it hits a risky action, then **pauses, surfaces the proposed action, and waits for a human**
to approve, edit, or reject — then resumes exactly where it stopped. It's only possible because state is
**checkpointed** (Lesson 3.1.03), so the pause can last seconds or hours. The architecture skill is the
**escalation trigger**: gate the few genuinely risky actions (money, sensitive ops, low confidence), not every
step — over-gating causes rubber-stamping, which is no control at all.

## ⚖️ Variations & When to Use
| Pattern | Use when | Avoid when → use instead | Gotcha |
|---|---|---|---|
| **`interrupt()` → resume** | any risky/irreversible action | trivial reversible steps → autonomous | **no checkpointer = can't resume** |
| **Escalation triggers** | money / sensitive / low-confidence | gating everything → fatigue | tune thresholds to real risk |
| **Async approval (webhook)** | approvers respond hours later | instant approvals → inline | needs a durable checkpointer |
| **Audit logging** | regulated (GDPR/finance) | — | record every decision (who/what/when) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Graph can't resume after approval | no checkpointer/thread_id | add a checkpointer (3.1.03) + `thread_id` |
| Approvers rubber-stamp everything | gating every step | gate **only** risky actions (escalation trigger) |
| Approval lost when human is slow | in-memory state | durable checkpointer + async resume |
| Compliance audit fails | no record of decisions | **audit-log** every approve/edit/reject |

## 📌 Quick Reference
- **Mechanism:** `interrupt(payload)` pauses + surfaces the action → `Command(resume=…)` injects the human's
  decision → graph continues. Requires a **checkpointer + `thread_id`**.
- **Gate by trigger:** dollar threshold · sensitive op · low confidence — not every step.
- **Audit everything** for compliance.

## 🛑 STOP — Self-Check
Should you put a human approval gate on **every** agent step, or only on **payments over $500**? Why — and what
makes the pause/resume possible?

<details><summary>Answer</summary>

**Only on payments over $500** (an **escalation trigger**). Autonomy where it's safe, a gate where it's risky.
Gating *every* step causes **alert fatigue** → humans rubber-stamp → the control becomes worthless. The
pause/resume is possible only because the graph state is **checkpointed** (Lesson 3.1.03): `interrupt()` saves
a checkpoint and stops; resuming reloads it and feeds the human's decision back in.
</details>

⏭️ **Next:** Module 3.6 — n8n workflow context.
