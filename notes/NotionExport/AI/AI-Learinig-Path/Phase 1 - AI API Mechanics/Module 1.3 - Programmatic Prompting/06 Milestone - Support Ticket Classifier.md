# 06 — Milestone: Support Ticket Classifier

> Phase 1 · Module 1.3 · Capstone project · ties together lessons 01–04

## 🗺️ What you're building

A **support-ticket classifier**: given a raw customer message, it extracts the **intent + entities**
as a validated **Pydantic model** and **routes the ticket to 1 of 5 departments** — then you
**benchmark accuracy across prompt variants** (zero-shot vs few-shot vs CoT). This is the Road Map's
Module 1.3 milestone, and it exercises everything in the module:

- **Structured outputs** (lesson 01) — the intent/entities/department schema.
- **Prompt templates** (lesson 02) — the classifier prompt, versioned.
- **Few-shot / CoT** (lesson 03) — the prompt variants you'll compare.
- **Context budget** (lesson 04) — keep the prompt + examples within the window.

## 🎯 The spec

1. Define a Pydantic result model: `intent`, extracted `entities`, a `department` (one of 5), and a
   `confidence`.
2. Classify a ticket into the model using `instructor` (auto-validated, auto-retry).
3. Build a tiny **labelled test set** and **measure accuracy** for at least **two prompt variants**.

## ⚙️ Scaffold (fill in the prompt + data)

```python
# pip install instructor pydantic
import instructor
from enum import Enum
from typing import List
from pydantic import BaseModel, Field

client = instructor.from_provider("openai/gpt-4o-mini")     # or ollama/... to run free & local

class Department(str, Enum):                 # exactly 5 routing targets
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    SALES = "sales"
    GENERAL = "general"

class Ticket(BaseModel):                     # the structured result (lesson 01)
    intent: str = Field(description="short phrase, e.g. 'refund request'")
    entities: List[str] = Field(description="key items: product, order id, dates")
    department: Department                   # the model must pick one of the 5
    confidence: float = Field(ge=0, le=1)

SYSTEM = "You route support tickets. Choose exactly one department."   # fixed instructions (no user text! lesson 02)

def classify(ticket_text: str) -> Ticket:
    return client.chat.completions.create(
        response_model=Ticket,               # validated Ticket back, not free text
        max_retries=3,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": ticket_text},   # untrusted text stays in the user turn
        ],
    )

# ---- benchmark across prompt variants (lesson 03) ----
labelled = [
    ("I was charged twice for order #4521", Department.BILLING),
    ("The app crashes when I upload a photo", Department.TECHNICAL),
    # ...add ~10-20 labelled tickets...
]

def accuracy() -> float:
    correct = sum(classify(text).department == gold for text, gold in labelled)
    return correct / len(labelled)

print(f"accuracy: {accuracy():.0%}")
```

## 🧪 The experiment (the point of the milestone)

Run `accuracy()` for **at least two prompt variants** and compare:
1. **Zero-shot** (the scaffold above).
2. **Few-shot** — add 3–5 example `ticket → department` pairs to the system prompt (lesson 03).
3. *(stretch)* **CoT** — ask it to reason about the category before deciding.

Note which variant scores best **and** its token cost — that trade-off *is* the lesson.

## ✅ Success criteria

- [ ] Returns a **valid `Ticket`** every time (never raw text / crashes) — structured outputs working.
- [ ] Routes to **exactly one of 5** departments.
- [ ] You measured **accuracy** for **≥2 prompt variants** and can say which won and why.
- [ ] No untrusted user text in the **system** prompt (injection-safe, lesson 02).

## 🚀 Stretch (toward the Phase 1 milestone)

- Wrap `classify` in a **FastAPI** endpoint with a `response_model` (Module 1.1).
- Add a **LiteLLM** fallback provider (Module 1.2 lesson 04) for resilience.
- **Stream** a longer explanation back via SSE (Module 1.1 lesson 04).

## 🛑 STOP — Self-Check

Why does returning a `Department` **enum** (not a free-text `department: str`) make this classifier
far more reliable to *route* on?

<details><summary>Answer</summary>

An **enum constrains the output to exactly the 5 valid departments**, and structured outputs +
validation guarantee the result is one of them — so your routing code can switch on it safely. A free
-text `str` could come back as "billing dept", "Billing", "finance", or a whole sentence, forcing
brittle string-matching and letting invalid values slip through. The enum turns "hope the text
matches" into "guaranteed one of five," which is the whole point of structured outputs here.
</details>

---
🎉 **Module 1.3 fully complete** (lessons 01–05 + this milestone). You've finished **all of Phase 1's
content**. Next: the **Phase 1 capstone milestone — a FastAPI AI Gateway** combining Modules 1.1–1.3.
