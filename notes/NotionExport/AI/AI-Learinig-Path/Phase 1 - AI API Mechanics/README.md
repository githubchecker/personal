# 🔷 Phase 1 — AI API Mechanics & Programmatic Prompting

Study notes for Phase 1 of the [Road Map](../AI%20Engineer%20Architect%20Road%20Map.md). Goal: build
production-grade AI service layers — talk to LLMs from code, stream, validate, and route across
providers.

> 🔑 New AI word? See the [AI Terms glossary](../AI%20Terms%20-%20Plain%20English%20Glossary.md).
> Built with the `topic-builder` skill: subtopics below are **JD-verified** (kept to what real job
> applications need), ordered by dependency, with optionals **labelled, not skipped**.

## 📋 JD-verified plan (validated against official docs, Jun 2026)

| Subtopic | Importance | JD signal | Notes from research |
| --- | --- | --- | --- |
| FastAPI basics (async, Pydantic models, auto-docs) | **MUST** | 82% | built on Starlette+Pydantic; used by MS/Uber/Netflix |
| Dependency Injection (`Depends`) | **MUST** | core | the FastAPI superpower for shared resources/auth |
| **Error handling & resilience** (HTTPException, timeouts, retries, fallback) | **MUST** | core | gap-add; clean errors + LLM-provider-failure resilience |
| SSE streaming (`StreamingResponse`) | **MUST** | 82% | LLM tokens streamed as Server-Sent Events |
| APIRouter / Middleware / CORS | SHOULD | — | structure + cross-cutting concerns |
| **Authentication & API security** (API key, OAuth2/JWT) | SHOULD | core | gap-add; secure the gateway, 401 vs 403, secrets hygiene |
| Config, Lifespan & Background Tasks | SHOULD | — | env secrets, **load model once at startup**, post-response work |
| Docker for AI services | **MUST** | 70% | layer caching, exec-form CMD, **memory = model × workers** |
| **Testing (pytest + TestClient)** | SHOULD | — | gap-add from docs; fake the LLM via dependency overrides |
| OpenAI SDK — **Chat Completions + Responses API** | **MUST** | 90% | ⚠️ Responses API is now primary; Chat Completions still supported |
| Anthropic (Claude) SDK | **MUST** | 90% | tool use, vision, prompt caching |
| Azure OpenAI (`AzureOpenAI`, deployments, managed identity) | **MUST** | 85% | enterprise data residency |
| LiteLLM multi-provider router | **MUST** | 85% | one interface + fallbacks |
| Ollama (local models) | SHOULD | 55% | privacy/offline |
| **Tool / function calling** | **MUST** | high | gap-add; the agent foundation — model requests, your code executes |
| Structured outputs (Pydantic + `instructor`) | **MUST** | 70% | force valid JSON from LLMs |
| CoT / ReAct prompting (incl. few-shot) | **MUST** | 75% | reasoning + the agent foundation; ReAct uses tool calling |
| Prompt templates & versioning | SHOULD | — | Jinja2, prompts-as-code, + prompt-injection safety |
| Context-window engineering | SHOULD | — | sliding window, summarisation |
| Concurrency/workers · gRPC · WebSockets · vLLM · DSPy | `[OPTIONAL]` | 25–35% | awareness only — see optional notes |
| File uploads (`UploadFile`, multipart) | SHOULD | — | deferred to **Phase 2** (RAG document/image ingestion) |
| Embeddings API (`embeddings.create` / `embed`) | **MUST** | — | deferred to **Phase 2** (RAG — embeddings + vector search) |

## Module 1.1 — AI Service Layer (FastAPI)
- [ ] [01 FastAPI Basics for AI Services](Module%201.1%20-%20AI%20Service%20Layer/01%20FastAPI%20Basics%20for%20AI%20Services.md)
- [ ] [02 Dependency Injection](Module%201.1%20-%20AI%20Service%20Layer/02%20Dependency%20Injection.md)
- [ ] [03 Error Handling & Resilience](Module%201.1%20-%20AI%20Service%20Layer/03%20Error%20Handling%20and%20Resilience.md)
- [ ] [04 Streaming with SSE](Module%201.1%20-%20AI%20Service%20Layer/04%20Streaming%20with%20SSE.md)
- [ ] [05 Structure — APIRouter, Middleware, CORS](Module%201.1%20-%20AI%20Service%20Layer/05%20Structure%20-%20APIRouter%20Middleware%20CORS.md)
- [ ] [06 Authentication & API Security](Module%201.1%20-%20AI%20Service%20Layer/06%20Authentication%20and%20API%20Security.md)
- [ ] [07 Config, Lifespan & Background Tasks](Module%201.1%20-%20AI%20Service%20Layer/07%20Config%20Lifespan%20and%20Background%20Tasks.md)
- [ ] [08 Testing (pytest + TestClient)](Module%201.1%20-%20AI%20Service%20Layer/08%20Testing%20with%20Pytest%20and%20TestClient.md)
- [ ] [09 Docker for AI Services](Module%201.1%20-%20AI%20Service%20Layer/09%20Docker%20for%20AI%20Services.md)
- [ ] [(Optional) 10 Production Extras — Workers, Rate Limiting, gRPC, WebSockets](Module%201.1%20-%20AI%20Service%20Layer/10%20Optional%20-%20Production%20Extras.md)
- [ ] [11 Milestone — Streaming AI Gateway](Module%201.1%20-%20AI%20Service%20Layer/11%20Milestone%20-%20Streaming%20AI%20Gateway.md)

## Module 1.2 — LLM APIs & Multi-Provider
- [ ] [01 OpenAI SDK — Chat Completions + Responses](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/01%20OpenAI%20SDK%20-%20Chat%20Completions%20and%20Responses.md)
- [ ] [02 Anthropic (Claude) SDK](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/02%20Anthropic%20Claude%20SDK.md)
- [ ] [03 Azure OpenAI](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/03%20Azure%20OpenAI.md)
- [ ] [04 LiteLLM Multi-Provider Router](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/04%20LiteLLM%20Multi-Provider%20Router.md)
- [ ] [05 Ollama (Local Models)](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/05%20Ollama%20Local%20Models.md)
- [ ] [06 Tool / Function Calling](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/06%20Tool%20and%20Function%20Calling.md)
- [ ] [(Optional) 07 vLLM — High-Throughput Self-Hosting](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/07%20Optional%20-%20vLLM.md)
- [ ] [08 Milestone — Multi-Provider LLM Router](Module%201.2%20-%20LLM%20APIs%20and%20Multi-Provider/08%20Milestone%20-%20Multi-Provider%20LLM%20Router.md)

## Module 1.3 — Programmatic Prompting
- [ ] [01 Structured Outputs (Pydantic + instructor)](Module%201.3%20-%20Programmatic%20Prompting/01%20Structured%20Outputs%20with%20Pydantic%20and%20Instructor.md)
- [ ] [02 Prompt Templates & Versioning](Module%201.3%20-%20Programmatic%20Prompting/02%20Prompt%20Templates%20and%20Versioning.md)
- [ ] [03 Reasoning Patterns — Few-shot, CoT & ReAct](Module%201.3%20-%20Programmatic%20Prompting/03%20Reasoning%20Patterns%20-%20Few-shot%20CoT%20and%20ReAct.md)
- [ ] [04 Context-Window Engineering](Module%201.3%20-%20Programmatic%20Prompting/04%20Context-Window%20Engineering.md)
- [ ] [(Optional) 05 DSPy — Programming, Not Prompting](Module%201.3%20-%20Programmatic%20Prompting/05%20Optional%20-%20DSPy.md)
- [ ] [06 Milestone — Support Ticket Classifier](Module%201.3%20-%20Programmatic%20Prompting/06%20Milestone%20-%20Support%20Ticket%20Classifier.md)

## Phase 1 Capstone — Integrative Project
The three **per-module milestones** above are the building blocks. The capstone **combines** them into
one service:
- [ ] **Streaming, multi-provider AI Gateway** — a FastAPI service (Module 1.1) that routes across
  providers with automatic failover (Module 1.2) and returns validated structured outputs / tools
  (Module 1.3): SSE streaming, per-user rate limiting, and token + cost logging per user. *(build after
  the module milestones)*
