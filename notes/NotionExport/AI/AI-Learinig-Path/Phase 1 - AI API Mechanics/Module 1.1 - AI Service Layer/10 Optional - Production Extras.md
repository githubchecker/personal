# 10 — (Optional) Production Extras

> Phase 1 · Module 1.1 · Lesson 10 · `[OPTIONAL — awareness]`

> 🟡 **Optional / awareness.** These appear in *some* JDs (mostly 25–40%) or specific stacks. Know
> **what each is and when to reach for it** — that's enough for Lead/Architect interviews. Go deep
> only when a role or project needs it.

## 🗺️ Stage 0 — Concept Map

A grab-bag of production concerns that surround the core AI service: scaling out, protecting it from
overuse, and alternative protocols. Each is a one-paragraph "know it exists" item that
builds on the rest of Module 1.1. (Authentication & security have their own lesson — 06.)

## 🔑 New Terms (plain English)

- **Worker / replication** — running multiple copies of your app to handle more traffic.
- **Rate limiting** — capping how many requests a caller may make (protects cost & stability).
- **gRPC** — a fast binary RPC protocol (alternative to REST) for service-to-service calls.
- **WebSocket** — a two-way, persistent connection (vs SSE's one-way stream).

## ⚙️ The extras (what + when)

### A. Workers & replication
One Uvicorn process can serve many concurrent requests. Under heavy load you run **more processes
("workers")** or **more containers**. *Rule from lesson 09:* each worker loads its own model copy,
so on a cluster prefer **one process per container** and scale by adding containers.
- *When:* you've outgrown a single process. *Formula (single box):* roughly `(2 × CPU cores) + 1`
  workers — but mind model memory.

### B. Rate limiting
Stop one caller (or a bug, or abuse) from flooding your **expensive** LLM endpoints. The common
FastAPI tool is **`slowapi`**.
```python
# pip install slowapi  — sketch
from slowapi import Limiter
limiter = Limiter(key_func=lambda r: r.client.host)
@app.get("/chat")
@limiter.limit("10/minute")          # max 10 calls/min per client
async def chat(): ...
```
- *When:* any public or cost-sensitive AI endpoint. **Highly recommended** even though it's "extra."

> **Auth & security** now have their own lesson — see [06 Authentication & API Security](06%20Authentication%20and%20API%20Security.md).

### C. gRPC `[OPTIONAL — niche, ~25% of JDs]`
A binary, contract-first RPC protocol. Faster and strongly-typed for **internal service-to-service**
calls, but harder to debug and not browser-friendly.
- *When:* a microservice estate already standardised on gRPC. Otherwise REST/FastAPI is the default.

### D. WebSockets `[OPTIONAL]`
Two-way persistent connection. SSE (lesson 04) already covers *streaming a reply*; reach for
WebSockets only when the **client must also stream live data back** (voice, collaborative/agent
sessions).
- *When:* bidirectional, real-time interaction — not just streaming output.

## 🧠 Common Misconceptions

- **"More workers always = faster."** → Not for AI: each worker copies the model into RAM; too many
  → out-of-memory. Scale containers, mind memory.
- **"Rate limiting is optional polish."** → For cost-sensitive LLM endpoints it's practically
  essential — one runaway loop can cost real money.
- **"Use WebSockets to stream the LLM reply."** → SSE is the simpler, correct tool for one-way
  streaming; WebSockets are for two-way.

## 📌 Quick Reference

- **scale:** more workers (single box, `(2×cores)+1`) **or** more containers (cluster) — memory = model × workers.
- **rate limit:** `slowapi` `@limiter.limit("10/minute")` — protect cost/stability.
- **auth:** see [lesson 06](06%20Authentication%20and%20API%20Security.md) (API key / OAuth2-JWT).
- **gRPC:** internal, typed, fast — niche; REST is the default.
- **WebSocket:** two-way; SSE is enough for one-way streaming.

## 🛑 STOP — Self-Check

For an AI chat API used by a public web app, which **two** of these extras would you prioritise, and
why?

<details><summary>Answer</summary>

**Rate limiting** and **scaling (workers/replication)**. Rate limiting protects you from a single
caller (or a bug) running up large **LLM costs** and degrading service; scaling keeps it responsive
under load. (Authentication is just as essential, but now has its own lesson — 06.) gRPC and
WebSockets are situational — gRPC is for internal service meshes, and SSE (lesson 04) already
handles streaming, so WebSockets aren't needed just to stream a reply.
</details>

---
🎉 **Module 1.1 (AI Service Layer) complete.** You can build, **handle errors**, **secure**, stream,
structure, configure, test, and containerize a FastAPI AI service. Next: **Module 1.2 — LLM APIs &
Multi-Provider** (OpenAI/Anthropic/Azure/LiteLLM/Ollama).
