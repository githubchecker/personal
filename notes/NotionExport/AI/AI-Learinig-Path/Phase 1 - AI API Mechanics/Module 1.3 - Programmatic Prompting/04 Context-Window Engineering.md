# 04 — Context-Window Engineering

> Phase 1 · Module 1.3 · Lesson 4 · `[SHOULD — managing the token budget]`

## 🗺️ Stage 0 — Concept Map

Every LLM call has a **fixed token budget** — the context window (Phase 0.0 lesson 0.0.5). Deciding
*what to put in it* is **context engineering**: fit the right information in, leave out the rest, and
control cost. It underpins chat memory, RAG (Phase 2), and cost/latency (Phase 4). Builds on 0.0.5 and
everything in Module 1.3.

## 🔑 New Terms (plain English)

- **Token budget** — `system + history + retrieved + output` must all fit in the **context window**.
- **Truncation** — dropping content (usually the oldest turns) to fit.
- **Sliding window** — keeping only the most recent *N* turns of a conversation.
- **Summarization** — compressing old history into a short summary to save tokens.
- **Lost-in-the-middle** — models attend best to the **start and end** of a long context, worst to the middle.
- **Prompt caching** — reusing a long, unchanging prefix cheaply on repeat calls.

## 🎈 Stage 1 — The Simple Idea (analogy: packing a small suitcase)

The context window is a **small suitcase**. You can't bring everything, so you **pack only what
matters** for this trip, **fold/compress** bulky items (summarize), and **leave behind** what you
don't need (truncate). Overpack and the lid won't close (you overflow the window) — or you pay excess
baggage (cost) for things you never use.

**The "Aha!":** more context isn't free or always better. The skill is choosing the **smallest set of
most-relevant tokens** — which is *why* RAG (retrieve a few relevant chunks) beats stuffing a whole
document in.

**💢 The old/painful way** — paste the whole document and the entire chat history into every call. You
hit context-overflow errors, pay for thousands of tokens you don't need, and trigger
**lost-in-the-middle**. Budgeting and compressing the context fixes all three.

## ⚙️ Stage 2 — How It Actually Works

### 4.1 The budget

```text
system prompt  +  conversation history  +  retrieved chunks  +  expected output   ≤   context window
```

Count tokens before sending (don't guess):

```python
# pip install tiktoken
import tiktoken
enc = tiktoken.get_encoding("o200k_base")
n_tokens = len(enc.encode(my_text))      # know your budget usage
```

### 4.2 Strategies to fit (and stay cheap)

**Fitting a long chat history — truncation vs sliding window vs summarization:**
- **Truncation** — drop the **oldest** turns when history grows.
  - **✅ Use when:** old detail is genuinely disposable (e.g. stateless one-off Q&A).
  - **🚫 Avoid when → use a sliding window + summary:** the chat must remember earlier facts or decisions.
  - **⚠️ Gotcha:** it permanently forgets what it drops, so the bot can contradict its earlier self.
- **Sliding window** — always keep the **last N** turns (plus the system prompt).
  - **✅ Use when:** general chat — recent turns matter most. A good default.
  - **🚫 Avoid when → add summarization:** important facts from *before* the window must persist.
  - **⚠️ Gotcha:** anything older than N turns is simply gone unless you also summarise it.
- **Summarization** — periodically replace old turns with a short **summary** ("user booking a flight to Tokyo, budget $1500…").
  - **✅ Use when:** long chats that must keep the gist of earlier context cheaply.
  - **🚫 Avoid when → use a plain window:** short chats — summarising adds an extra LLM call for little gain.
  - **⚠️ Gotcha:** the summary can lose or distort details, and it costs an extra call to produce.

> In practice you **combine** them: a sliding window of recent turns verbatim (word-for-word) **plus** a
> running summary of everything before it.

**Other levers:**
- **Prioritise placement:** put the **most important** info at the **start or end**, not buried in the
  middle (**lost-in-the-middle**).
- **Retrieve, don't stuff (RAG — Phase 2):** instead of pasting a 50-page manual, fetch the 3 relevant
  paragraphs. Smaller, cheaper, *and* more accurate.
- **Long-context models (128K–1M+ tokens):** having room to dump everything in is tempting, but you
  still **pay per token** and still hit lost-in-the-middle. Rule of thumb: **full context** for a
  single moderate document used wholesale; **chunked RAG** for large, many, or frequently-queried
  corpora (document collections).

### 4.3 Cost & latency (and prompt caching)

Fewer tokens = **cheaper and faster** (you pay per input + output token). For a long, **unchanging**
prefix (a big system prompt or document reused across calls), **prompt caching** (OpenAI/Anthropic)
lets the provider reuse it at a large discount instead of re-billing it every call.

```python
# Conceptual: a 2,000-token system prompt reused on every request ->
# prompt caching charges it once and serves cached hits cheaply on subsequent calls.
```

**Order matters for caching (the KV cache — the model's reusable store of already-processed tokens).**
Providers cache from the **start** of the prompt up to the first token that changes. So put **stable**
content (system prompt, fixed context) **first** and **variable** content (the user's new message)
**last** — that **maximises cache hits** and cuts cost and latency.

> 🔬 **Under the hood:** the model is **stateless** — it has no memory between calls. "Memory" is just
> the tokens you re-send each time, so fitting the budget = *choosing and compressing* which tokens to
> resend (truncate / summarise / retrieve). **Prompt caching** lets the provider reuse a fingerprinted
> (hashed), unchanging prefix at a discount instead of re-billing it every call.

## 🚀 Stage 3 — In Practice / Why It Matters

This is the day-to-day craft of building chat and RAG systems: keep a **sliding window + summary** for
chat memory, **retrieve** the few relevant chunks for RAG, **count tokens** to avoid overflow errors,
and **cache** big static prefixes to cut cost. It directly drives the cost and quality numbers you'll
own in Phases 2 and 4.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Fit a long history** | truncation vs sliding window vs summarization | **sliding window** (recent turns) + a **summary** of older ones for chat memory · plain truncation only if old detail is disposable |
| **Big knowledge** | stuff full context vs **RAG retrieval** | **retrieve** the few relevant chunks (cheaper, more accurate, avoids lost-in-the-middle) · full context only for one moderate doc used wholesale |
| **Repeated prefix** | re-send vs **prompt caching** | **cache** a big static prefix (system prompt/doc), stable content first to maximise hits |
| **Counting** | guess vs **`tiktoken`** | always **count** before sending to avoid `context_length_exceeded` |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `context_length_exceeded` error | Sent more tokens than the window | Count tokens; truncate/summarize/retrieve |
| Costs balloon | Stuffing huge prompts every call | Send only relevant tokens; cache static prefixes |
| Model "ignores" buried info | Lost-in-the-middle | Move key info to the start/end |
| Chat "forgets" early context | Naive truncation dropped it | Summarize old turns instead of dropping them |
| Slow responses | Oversized context | Trim input; smaller context = faster |

## 📌 Quick Reference

```text
system + history + retrieved + output  ≤  context window
```
- **Count** tokens (`tiktoken`) · **fit** via truncation / sliding window / summarization / retrieval.
- **Lost-in-the-middle:** key info at start/end · **prompt caching:** reuse big static prefixes cheaply.
- Smaller, relevant context = **cheaper, faster, often more accurate** (why RAG beats stuffing).

> 🎯 **Interview angle:** "How do you handle a conversation longer than the context window?" → manage
> the token budget: keep a **sliding window** of recent turns plus a running **summary** of older
> ones, count tokens to avoid overflow, place key info at the start/end (lost-in-the-middle), and use
> retrieval/caching to stay small and cheap.

## 🛑 STOP — Self-Check

A chatbot conversation has grown past the model's context window. You must keep it coherent without
overflowing. Why is **summarizing** the old turns usually better than just **truncating** (dropping)
them?

<details><summary>Answer</summary>

**Truncation throws the old turns away**, so the model permanently **forgets** earlier facts (the
user's name, their goal, decisions made) — the chat becomes incoherent. **Summarization compresses**
those old turns into a short recap that still **fits the budget** but **preserves the gist**, so the
model keeps the important context at a fraction of the tokens. You typically combine both: a **sliding
window** of recent turns verbatim **plus a running summary** of everything before it.
</details>
