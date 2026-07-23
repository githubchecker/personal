# 02 — Anthropic (Claude) SDK

> Phase 1 · Module 1.2 · Lesson 2 · `[JD VERIFIED — 90%]`

## 🗺️ Stage 0 — Concept Map

Claude (by Anthropic) is the **second** provider named in ~90% of AI-engineer JDs, and many teams use
it alongside OpenAI for cost, quality, or resilience reasons. The idea is identical to lesson 01 —
send messages, get text — but the **shape differs** in three ways worth knowing. This sets up the
multi-provider router (lesson 04), which papers over those differences.

> 🔑 Model names like `claude-opus-4-6` are current examples (2026) — check Anthropic's live list.

## 🔑 New Terms (plain English)

- **Anthropic / Claude SDK** — the official Python library for Claude models (`pip install anthropic`).
- **Messages API** — Claude's main call: `client.messages.create(...)`.
- **`max_tokens`** — the **maximum length** of the reply; with Claude this is **required**.
- **`system` parameter** — Claude's instructions go in a **separate top-level argument**, not as a message.
- **Content block** — Claude's reply is a **list** of blocks (text, tool use, image), not a bare string.
- **`stop_reason`** — why generation ended: `end_turn` · `max_tokens` · `stop_sequence` · `tool_use`.
- **Extended thinking** — a mode where Claude reasons internally first (`thinking={"type":"enabled","budget_tokens":N}`).
- **Prompt caching** — marking a long, reused prefix with `cache_control` so repeats are ~90% cheaper.
- **`usage`** — token counts on the reply (`input_tokens` / `output_tokens`, plus cache counts).

## 🎈 Stage 1 — The Simple Idea (analogy: a different expert, different intake form)

Same kind of expert call as OpenAI, but this expert uses a slightly different **intake form**: you
must say **upfront how long an answer you'll allow** (`max_tokens`), the **house rules** go in a
separate box (`system=`), and the reply comes back as a **stack of cards** (content blocks) rather
than one sheet of paper.

**The "Aha!":** the *concept* is identical to OpenAI; only the *parameters and response shape*
change. Learn the three differences and you can call Claude.

**💢 Without the SDK (the old/painful way)** — same raw-HTTP pain as any provider: build the POST, set the
`x-api-key` / `anthropic-version` headers, and parse Claude's block-shaped JSON by hand. The SDK
handles all that — you just learn the three shape differences below.

## ⚙️ Stage 2 — How It Actually Works

### 2.1 Install & set the key

```powershell
pip install anthropic python-dotenv
```
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 2.2 A basic Claude call (spot the 3 differences)

```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,                       # (1) REQUIRED — cap the reply length
    system="You are a concise assistant.", # (2) instructions are a SEPARATE param, not a message
    messages=[
        {"role": "user", "content": "Explain what an API is in one sentence."},
    ],
)
print(message.content[0].text)             # (3) reply is a LIST of blocks — text is in .content[0].text
```

The three differences vs OpenAI:
1. **`max_tokens` is required** (OpenAI makes it optional).
2. **`system=` is top-level** (OpenAI uses a `system`/`developer` *message*).
3. **`message.content` is a list of blocks** (OpenAI gives `.choices[0].message.content` as a string).

### 2.3 The parameters that matter (full syntax)

```python
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,            # REQUIRED — also the hard cap on output (cost/latency control)
    system="You are concise.",  # persona / rules (top-level)
    messages=[...],
    temperature=0.7,            # 0 = deterministic … 1.0 = creative (Claude's range is 0–1)
    top_p=0.9,                  # nucleus sampling (an alternate randomness control) — tune temperature OR top_p
    top_k=40,                   # (rarely used) limit to the K most likely tokens
    stop_sequences=["\n\nHuman:"],  # stop generating if this text appears
)
```

### 2.4 Reading the response (blocks, stop_reason, usage)

```python
message.content            # a LIST of blocks — text lives in blocks of type "text"
message.content[0].text    # the text of the first block
message.stop_reason        # WHY it stopped: "end_turn" | "max_tokens" | "stop_sequence" | "tool_use"
message.usage.input_tokens, message.usage.output_tokens   # for cost tracking (log these)
```

`stop_reason == "max_tokens"` means the reply was cut off — raise `max_tokens`. `"tool_use"` means
Claude wants to call a tool (2.8).

### 2.5 Async + streaming

```python
from anthropic import AsyncAnthropic
client = AsyncAnthropic()

async def ask(prompt: str) -> str:
    msg = await client.messages.create(
        model="claude-opus-4-6", max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

# streaming uses a context manager that also assembles the final message for you:
with client.messages.stream(model="claude-opus-4-6", max_tokens=512,
                            messages=[{"role": "user", "content": "Write a haiku."}]) as stream:
    for text in stream.text_stream:        # text pieces as they arrive -> forward as SSE (1.1 L04)
        print(text, end="", flush=True)
    final = stream.get_final_message()     # the complete Message once streaming ends
```

### 2.6 Extended thinking — for hard reasoning

Claude can **reason internally before answering** (better on math/logic/multi-step). Turn it on with a
token budget (must be **less than `max_tokens`**):

```python
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    thinking={"type": "enabled", "budget_tokens": 2000},   # reserve up to 2000 tokens to "think"
    messages=[{"role": "user", "content": "Solve this step by step: ..."}],
)
# the reply now includes a "thinking" block (the reasoning) before the final "text" block.
```

**Extended thinking — on vs off (pick one):**
- **On** (`thinking={"type":"enabled", ...}`)
  - **✅ Use when:** hard, multi-step problems — maths, logic, planning, careful analysis.
  - **🚫 Avoid when → leave it off:** simple or short calls — the extra reasoning tokens cost time and money for no gain.
  - **⚠️ Gotcha:** `budget_tokens` must be **less than `max_tokens`**, and you pay for the thinking tokens too.
- **Off** (default)
  - **✅ Use when:** everyday calls — chat, extraction, short answers.
  - **🚫 Avoid when → turn it on:** the model keeps getting genuinely multi-step problems wrong.
  - **⚠️ Gotcha:** with thinking off, a hard problem can get a confident-but-wrong one-shot answer.

### 2.7 Vision — images as content blocks

Send an image by making the user content a **list of blocks** (text + image):

```python
message = client.messages.create(
    model="claude-opus-4-6", max_tokens=512,
    messages=[{"role": "user", "content": [
        {"type": "text", "text": "What's in this image?"},
        {"type": "image", "source": {"type": "base64",
                                     "media_type": "image/jpeg", "data": b64_string}},
        # or a URL source: {"type": "url", "url": "https://…/cat.jpg"}
    ]}],
)
```

### 2.8 Tool use — the Claude shape (full mechanics in lesson 06)

Same idea as OpenAI tool calling, different shape: pass `tools`, and when Claude wants one the reply's
`stop_reason` is `"tool_use"` with a `tool_use` block; you run it and reply with a `tool_result` block:

```python
resp = client.messages.create(
    model="claude-opus-4-6", max_tokens=1024,
    tools=[{"name": "get_weather", "description": "...",
            "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}}}],
    messages=[{"role": "user", "content": "Weather in Paris?"}],
)
if resp.stop_reason == "tool_use":
    call = next(b for b in resp.content if b.type == "tool_use")
    result = get_weather(**call.input)          # YOU run it
    follow = client.messages.create(             # send the result back as a tool_result
        model="claude-opus-4-6", max_tokens=1024,
        messages=[
            {"role": "user", "content": "Weather in Paris?"},
            {"role": "assistant", "content": resp.content},
            {"role": "user", "content": [{"type": "tool_result",
                                          "tool_use_id": call.id, "content": result}]},
        ],
    )
```

### 2.9 Prompt caching — cheap repeats of a long prefix

If you reuse a **big** system prompt or document across calls, mark it with `cache_control` so repeats
read it from cache at **~90% lower cost** (and lower latency):

```python
message = client.messages.create(
    model="claude-opus-4-6", max_tokens=512,
    system=[{"type": "text", "text": LONG_INSTRUCTIONS,
             "cache_control": {"type": "ephemeral"}}],   # cache this block
    messages=[{"role": "user", "content": "..."}],
)
# usage.cache_creation_input_tokens (first call) vs usage.cache_read_input_tokens (cached hits)
```

**Prompt caching — cache vs don't (pick one):**
- **Cache** (`cache_control` on a block)
  - **✅ Use when:** a **big**, unchanging prefix is reused across many calls — a long system prompt, a document, or few-shot examples.
  - **🚫 Avoid when → don't cache:** short or one-off prompts — the cache write costs more than it saves.
  - **⚠️ Gotcha:** the cache is short-lived (ephemeral) and keyed by *exact* content — one character change misses the cache.
- **Don't cache** (default)
  - **✅ Use when:** prompts are short, unique, or rarely repeated.
  - **🚫 Avoid when → cache:** you re-send the same large prefix every call (you're paying full price each time).

> 🔬 **Under the hood:** `content` is a **list of typed blocks** because Claude can mix together
> (interleave) text, tool-use, and images in one reply — the SDK hands you those blocks as-is.
> `max_tokens` reserves the output budget up front (which is why it's required). **Prompt caching**
> stores the *tokenised* prefix (the prompt already split into tokens) on Anthropic's side, keyed by the
> block's content, so a repeat call skips re-processing it — hence the ~90% discount.

## 🚀 Stage 3 — In Practice / Why It Matters

Teams rarely bet on one provider. They use Claude and GPT **interchangeably** — switching for price,
quality on a given task, or when one is down. Knowing both SDKs (and that they differ only in shape)
is exactly what the multi-provider router in lesson 04 automates, and what "provider-agnostic"
(works with any provider) architecture in JDs means.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Provider** | Claude vs GPT (OpenAI) | Claude for long context (~200K), strong writing/reasoning, or as a failover (a backup when the other is down) · GPT for the Responses API & tooling ecosystem. Most teams support **both** (lesson 04) |
| **Thinking** | extended thinking on vs off | **on** for hard multi-step reasoning · **off** for simple/short calls (saves tokens + latency) |
| **Prompt caching** | cache vs don't | **cache** a big, reused system prompt/document (~90% cheaper repeats) · skip for short/one-off prompts |
| **Streaming** | `.stream()` helper vs raw `stream=True` | the **`.stream()` context manager** (assembles the final message, simpler) for most cases |
| **`temperature` vs `top_p`** | one or the other | tune **one**, not both — `temperature` for everyday use |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `TypeError`/400: `max_tokens` required | Omitted `max_tokens` | Always pass `max_tokens=...` |
| `system` had no effect | Put it as a message | Use the top-level `system=` parameter |
| `AttributeError`/odd output on the reply | Treated `.content` as a string | Read `message.content[0].text` (list of blocks) |
| `AuthenticationError` | Key missing/wrong | Set `ANTHROPIC_API_KEY` in `.env` |
| Reply cut off mid-sentence | `max_tokens` too small | Raise `max_tokens` |

## 📌 Quick Reference

```python
from anthropic import Anthropic
client = Anthropic()

msg = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,                 # REQUIRED (also the output cap)
    system="You are concise.",       # top-level (not a message)
    messages=[{"role": "user", "content": "..."}],
    temperature=0.7,                 # or top_p — not both
)
msg.content[0].text                  # reply = list of blocks · msg.stop_reason · msg.usage.input_tokens
# async: AsyncAnthropic()  ·  stream: client.messages.stream(...)  ·  hard reasoning: thinking={...}
# vision: image block in content  ·  tools: stop_reason=='tool_use' (L06)  ·  cache: cache_control on a big system block
```
- 3 differences vs OpenAI: **`max_tokens` required** · **`system=` top-level** · **reply is content blocks**.
- Extras: **extended thinking** (hard reasoning) · **vision** (image blocks) · **prompt caching** (cheap reused prefix) · track **`usage`**.

> 🎯 **Interview angle:** "Differences between the OpenAI and Anthropic SDKs?" → same concept
> (messages → text), but Claude **requires `max_tokens`**, takes **`system` as a top-level param**,
> and returns a **list of content blocks** instead of a single string.

## 🛑 STOP — Self-Check

You copy your working OpenAI call and just swap in the Anthropic client, passing `system` as the first
message and no `max_tokens`. Name the two things that will go wrong.

<details><summary>Answer</summary>

(1) **It will error because `max_tokens` is required** for Claude's Messages API — you must pass it.
(2) **The `system` instruction will be ignored** (or misformatted) because Claude expects `system` as
a **separate top-level parameter**, not as a message in the `messages` list. (And when you read the
reply, remember it's `message.content[0].text`, a list of blocks — not a plain string.)
</details>
