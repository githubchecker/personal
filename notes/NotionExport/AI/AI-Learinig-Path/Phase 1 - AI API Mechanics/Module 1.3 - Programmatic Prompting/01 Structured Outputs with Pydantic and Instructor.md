# 01 — Structured Outputs (Pydantic + instructor)

> Phase 1 · Module 1.3 · Lesson 1 · `[JD VERIFIED — 70%]`

## 🗺️ Stage 0 — Concept Map

An LLM returns **free text** — but your program needs **reliable, typed data** (a price as a `float`,
a category from a fixed set) to *do* anything with it. **Structured outputs** force the model to
return JSON that matches a schema you define, validated automatically. This is the bridge between
"the model said something" and "my code can use it." Builds directly on Phase 0.1 Pydantic (lesson
13) and the provider SDKs (Module 1.2). It's in ~70% of JDs.

## 🔑 New Terms (plain English)

- **Structured output** — model output forced to match a fixed shape (JSON), not free prose.
- **JSON Schema** — a machine-readable description of that shape (fields + types).
- **`response_format` / `.parse()`** — OpenAI's native way to get a typed object back.
- **`instructor`** — a library that returns a **validated Pydantic object** from many providers, with
  automatic retries.
- **`response_model`** — the Pydantic class you ask `instructor` to fill.
- **Re-ask / retry** — when the output fails validation, the library sends the error back to the model
  and asks again.
- **`Field(description=...)`** — a per-field hint the model reads to fill it correctly.
- **`Literal` / `Enum`** — constrain a field to a fixed set of allowed values.
- **`Partial[Model]`** — a progressively-filled version of your model for streaming.

## 🎈 Stage 1 — The Simple Idea (analogy: a form vs a free essay)

Asking an LLM a question normally gets you a **free essay** — readable, but a pain to parse reliably.
Structured outputs hand the model a **fill-in-the-blank form** (your Pydantic model) and get back the
**completed form**, guaranteed to have the right fields and types.

**The "Aha!":** you stop *parsing* the model's prose and start *defining the shape you want* — the
model fills it in, and the library validates it before your code ever sees it.

## ⚙️ Stage 2 — How It Actually Works

### 1.1 The problem (the brittle old way)

```python
reply = "The user is John, age 30."          # free text from the model
# ...now YOU write fragile regex/splitting to pull out name + age, and hope the format never changes.
```

### 1.2 Native OpenAI structured outputs (`.parse()`)

Define a **Pydantic model**, hand it to `parse`, get a **typed object** back:

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class User(BaseModel):       # the SHAPE you want
    name: str
    age: int

completion = client.chat.completions.parse(    # note: .parse, not .create
    model="gpt-5.5",
    messages=[{"role": "user", "content": "Extract: John is a 30-year-old engineer."}],
    response_format=User,                      # force output to match User
)
user = completion.choices[0].message.parsed    # <- a real User instance
print(user.name, user.age)                     # John 30   (typed!)
```

The model is constrained to emit JSON that fits `User`, and the SDK parses it into the object.

### 1.3 `instructor` — multi-provider + automatic retries (the workhorse)

`instructor` does the same across **15+ providers** and **re-asks the model** when validation fails:

```python
# pip install instructor
import instructor
from pydantic import BaseModel, field_validator

client = instructor.from_provider("openai/gpt-4o-mini")   # or "anthropic/...", "ollama/..." (Module 1.2)

class User(BaseModel):
    name: str
    age: int

    @field_validator("age")
    @classmethod
    def age_positive(cls, v):
        if v < 0:
            raise ValueError("age must be positive")       # if violated, instructor RE-ASKS the model
        return v

user = client.chat.completions.create(
    response_model=User,                  # ask for a validated User
    messages=[{"role": "user", "content": "John is 30 years old."}],
    max_retries=3,                        # auto-retry on validation failure
)
print(user)                               # User(name='John', age=30)  — already validated
```

- **`response_model=User`** → you get a `User` instance, not raw text.
- **`max_retries=3`** → on a validation error, instructor feeds the error back and the model fixes it.
- **Same code for any provider** (it builds on the Module 1.2 idea), plus streaming partials
  (`Partial[User]`) and lists (`create_iterable`).

> 🔎 **You'll also see `instructor.patch(client)`** in older code — the legacy way to add `response_model`
> to an existing OpenAI client. The newer `from_provider(...)` above is the same idea, multi-provider.
> Under the hood, instructor enforces the schema using each provider's native mechanism — JSON-schema on
> OpenAI, **tool-use on Anthropic** — so you get a validated object the same way everywhere.

### 1.4 Nested schemas — reasoning chains & extraction pipelines

Real extraction is rarely flat. Pydantic models **nest**, so one call returns a whole structure:

```python
from typing import List
from pydantic import BaseModel

class LineItem(BaseModel):
    description: str
    amount: float

class Invoice(BaseModel):                 # a model made of OTHER models + a list
    vendor: str
    items: List[LineItem]                 # nested list of LineItem
    total: float

invoice = client.chat.completions.create(
    response_model=Invoice,               # the model fills the WHOLE nested structure
    messages=[{"role": "user", "content": raw_invoice_text}],
    max_retries=3,
)
print(invoice.items[0].description)        # fully typed, all the way down
```

This is how **extraction pipelines** (documents → structured records) and **reasoning chains** (a
`steps: List[Step]` field) are built — one schema, one validated object.

### 1.5 Guide the model: field descriptions, enums, optionals

The schema isn't just validation — it **tells the model what to produce**. Rich fields = better fills:

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    summary: str = Field(description="one-line summary of the issue")        # description guides the model
    priority: Literal["low", "medium", "high"]                              # FIXED choices -> no invalid values
    assignee: Optional[str] = Field(None, description="name, or null if unknown")  # optional field
```

- **`Field(description=...)`** — the model reads it; clear descriptions sharply improve accuracy.
- **`Literal[...]` / `Enum`** — constrain a field to a fixed set (classification, routing) so the
  model *can't* return an off-list value.
- **`Optional[...]`** — let the model say "unknown" instead of hallucinating a value.

### 1.6 Streaming partials & extracting lists

For a live UI, stream the object as it fills; to pull many records, ask for a list:

```python
from instructor import Partial

for partial in client.chat.completions.create(          # progressively-filled object
        response_model=Partial[User], stream=True, messages=[...]):
    print(partial)   # User(name=None,...) -> User(name='John', age=None) -> User(name='John', age=30)

users = client.chat.completions.create(                 # extract a LIST of items
    response_model=list[User], messages=[{"role": "user", "content": "John 30, Mary 25"}])
```

### 1.7 Native vs instructor — which to use

- **Native `.parse()`** (OpenAI SDK built-in)
  - **Key features:** no extra dependency; returns a typed object via `response_format`.
  - **✅ Use when:** you're OpenAI-only and want a simple one-shot extraction with zero extra libraries.
  - **🚫 Avoid when → use `instructor`:** you need multiple providers, auto re-ask on validation failure, or streaming partials.
  - **⚠️ Gotcha:** it's OpenAI-specific — the same code won't run against Claude/Ollama.
- **`instructor`** (`from_provider(...)`)
  - **Key features:** one interface for 15+ providers; auto-retry on validation error; streaming partials; list extraction.
  - **✅ Use when:** multi-provider portability, you want the library to re-ask on bad output, or you stream the object as it fills.
  - **🚫 Avoid when → use native:** a quick OpenAI-only script where one extra dependency isn't worth it.
  - **⚠️ Gotcha:** retries cost extra model calls — cap `max_retries` and keep schemas tight.

### 1.8 How the shape is enforced (json_schema vs JSON mode vs tool-calling)

Under the surface, a provider can force structure three ways — `instructor` picks the best per
provider, but it's worth knowing which is which:

- **Strict `json_schema`** (constrained decoding)
  - **✅ Use when:** available (modern OpenAI) — it **guarantees** the output matches your schema exactly.
  - **🚫 Avoid when → fall back to tool-calling:** the provider/model doesn't support strict schema.
  - **⚠️ Gotcha:** very deeply nested or exotic schemas may not be fully supported — keep them reasonable.
- **JSON mode** (`response_format={"type":"json_object"}`)
  - **✅ Use when:** you just need *valid JSON* and will check the fields yourself.
  - **🚫 Avoid when → use json_schema:** you need the *exact* fields/types guaranteed, not just "some JSON."
  - **⚠️ Gotcha:** it guarantees JSON *syntax*, **not** that your fields/types are right — still validate.
- **Tool-calling** (your schema as a tool's parameters)
  - **✅ Use when:** the provider lacks strict schema but supports tools (e.g. Anthropic) — instructor uses this.
  - **🚫 Avoid when → use json_schema:** strict schema is available and simpler.
  - **⚠️ Gotcha:** it's the Module 1.2 tool-call mechanism underneath, so the same validation caveats apply.

> 🔬 **Under the hood:** with **strict json_schema** the provider constrains *decoding* (how it picks
> each next token) — at each step
> it only allows tokens that keep the JSON valid against your schema, so the output **can't** break the
> shape. `instructor` converts your Pydantic model → JSON schema, sends it via the provider's native
> mechanism (json_schema on OpenAI, tool-use on Claude), then **validates** the parsed result; on a
> `ValidationError` it appends the error and re-asks (`max_retries`).

## 🚀 Stage 3 — In Practice / Why It Matters

Structured outputs are how you get **classification labels**, **extracted entities**, **tool
arguments**, and **typed API responses** you can trust. They pair perfectly with FastAPI's
`response_model` (Module 1.1): the LLM fills a Pydantic model, you return that same model. This is the
difference between a demo that string-parses and a service that reliably feeds LLM output into the
next system.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Library** | native `.parse()` vs **`instructor`** | native for OpenAI-only, no deps · **instructor** for multi-provider + auto-retry + streaming partials |
| **Enforcement mode** | json_schema (strict) vs JSON mode vs tool-calling | prefer **strict json_schema** (guaranteed shape) where supported; instructor picks the best per provider |
| **Fixed choices** | free `str` vs `Literal`/`Enum` | **`Literal`/`Enum`** for categories/routing — the model can't go off-list |
| **Missing data** | required vs `Optional` | **`Optional`** (null) so the model says "unknown" instead of inventing a value |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Fragile regex to read the reply | Parsing free text by hand | Define a Pydantic model + structured output |
| `ValidationError` not handled | No retry on bad output | Use `instructor` with `max_retries=…` (it re-asks) |
| Output ignores your schema | Used plain `create` without a schema | Use `.parse(response_format=…)` or `response_model=…` |
| Works on OpenAI, breaks elsewhere | Native parse is provider-specific | Use `instructor.from_provider(...)` for portability |
| Model returns extra prose | Asked for text, not structured | Always pass the model/`response_model` |

## 📌 Quick Reference

```python
# Native (OpenAI):
client.chat.completions.parse(model=..., messages=[...], response_format=MyModel).choices[0].message.parsed

# instructor (multi-provider + retries):
client = instructor.from_provider("openai/gpt-4o-mini")
obj = client.chat.completions.create(response_model=MyModel, messages=[...], max_retries=3)
```
- Define a **Pydantic model** = the shape · get a **typed, validated object** back · **`max_retries`** auto-fixes bad output.

> 🎯 **Interview angle:** "How do you get reliable JSON out of an LLM?" → define a Pydantic schema and
> use structured outputs — OpenAI's `.parse()`/`response_format`, or `instructor`'s `response_model`
> with `max_retries` (which re-asks the model with the validation error) for multi-provider + retries.

## 🛑 STOP — Self-Check

Your prompt asks the model for a user's `age`, but it sometimes returns `-5` or `"thirty"`. How do
structured outputs (with `instructor`) make sure your code only ever receives a valid positive
integer?

<details><summary>Answer</summary>

You define a Pydantic model with `age: int` and a `@field_validator` that rejects negatives. With
`instructor` and `response_model=User` + `max_retries`, the output is **parsed and validated** before
you get it: `"thirty"` fails the `int` type and `-5` fails the validator, so instructor **re-asks the
model with the error message**, and the model corrects itself. Your code only ever receives a valid
`User` — invalid output never reaches it.
</details>
