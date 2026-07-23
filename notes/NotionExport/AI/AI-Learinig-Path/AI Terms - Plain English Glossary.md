# AI Terms — Plain-English Glossary

A quick, beginner-first reference for the Python module. Whenever a lesson mentions an AI word you
don't know yet, look it up here — one or two plain lines, no jargon-inside-jargon. (Deeper coverage
comes in **Phase 0.0** and later phases; this is just enough to follow the current lesson.)

## The absolute basics
- **AI model / model** — a program that "learned" patterns from lots of data. Give it an input, it
  produces an output. Think of a very advanced auto-complete.
- **LLM (Large Language Model)** — the kind of AI behind ChatGPT, Claude, Gemini. You send it text
  (a *prompt*); it sends text back. "Large" = trained on enormous amounts of text.
- **Prompt** — the text you send to an LLM (your question or instruction).
- **Inference** — using a trained model to get an answer (as opposed to *training* it). Running the
  model = inference.
- **Parameters / weights** — the millions of numbers inside a model that store what it learned.
  More parameters ≈ more capable, but slower and costlier.

## Text in, numbers out
- **Token** — a small piece of text the model actually reads (often a word or part of a word).
  Models count and bill in tokens, not words. Rough rule: 1 token ≈ 0.75 words.
- **Context window** — the most text (in tokens) a model can look at in one go. Go over it and the
  oldest text drops out of view.
- **Chunk / chunking** — splitting a big document into smaller pieces so each fits the model and can
  be searched individually.
- **Tensor** — a grid of numbers (1-D = a list, 2-D = a table, 3-D = a stack of tables). The basic
  data unit in AI math libraries like NumPy and PyTorch (Module 0.2).
- **Logits** — the **raw scores** a model outputs for every possible next word, *before* they're
  turned into probabilities.
- **Softmax** — the function that turns logits into **probabilities that add up to 100%** (so one
  next word can be picked).

## Meaning as numbers
- **Vector** — simply a list of numbers, e.g. `[0.9, 0.1, 0.0]`. Picture it as coordinates, or an
  arrow pointing somewhere in space.
- **Embedding** — a vector that captures the *meaning* of a piece of text, produced by a model.
  Similar meanings → vectors that sit close together.
- **Vector space** — the imaginary "map" where embeddings live; nearby points mean similar things.
- **Cosine similarity** — a score from `-1` to `1` for how alike two vectors are by their
  **direction**: `1` = same meaning, `~0` = unrelated, `-1` = opposite.

## Search & retrieval
- **Semantic search** — finding text by *meaning* instead of exact keyword matching, using
  embeddings + similarity.
- **Vector database** — a specialised store for millions of embeddings that instantly returns the
  ones nearest to a query vector (semantic search at scale). Examples: pgvector, Pinecone, Qdrant.
- **Retrieval** — the step of fetching the most relevant pieces of text for a question.
- **Top-k retrieval** — fetching the *k* most relevant chunks for a query (e.g. top-5).
- **Corpus / knowledge base** — the whole collection of documents your RAG system can draw on.
- **RAG (Retrieval-Augmented Generation)** — fetch relevant text (retrieval), then hand it to an LLM
  so it answers from *your* data instead of guessing.
- **Grounding** — basing a model's answer on real, provided sources (reduces made-up answers).
- **Hallucination** — when a model confidently states something false. Grounding/RAG help prevent it.

## RAG pipeline & quality (Phase 2)
- **OCR (Optical Character Recognition)** — turning an image of text (a scan) into real characters,
  so scanned PDFs can be searched.
- **Matryoshka embedding** — an embedding you can safely **shorten** (e.g. 3072 → 256 numbers) to save
  storage/speed with little quality loss — smaller versions nest inside the big one.
- **MTEB** — *Massive Text Embedding Benchmark*; a public leaderboard ranking embedding models by task.
- **Recall@K** — of all the genuinely relevant chunks, how many appeared in the top-k retrieved
  (the main retrieval-quality metric).
- **MRR (Mean Reciprocal Rank)** — how high up the *first* correct chunk ranks, averaged over queries.

## Vector infrastructure & advanced search (Phase 2.2–2.4)
- **ANN (Approximate Nearest Neighbour)** — fast "close-enough" nearest-vector search; trades a little
  accuracy for big speed at scale.
- **HNSW** — a multi-layer *graph* index for vectors: best speed/accuracy, heavier on memory (the default).
- **IVFFlat** — a *buckets* vector index: groups vectors and searches the nearest few buckets; lighter, slightly less accurate.
- **Namespace** *(Pinecone)* — a partition inside one index to keep tenants/customers separate.
- **Payload** *(Qdrant)* — the metadata attached to a stored vector (`{"dept": "HR"}`).
- **Quantization** — compressing vectors (e.g. to 1 byte each) to cut memory ~4×, with a small recall loss.
- **Egress** — the fee a cloud charges for data **leaving** a region/provider; avoid it by keeping things in one region.
- **Sparse vs dense retrieval** — sparse = exact-word match (**BM25**); dense = meaning match (embeddings).
- **BM25** — the classic keyword-ranking algorithm; great for exact IDs/codes/names dense search misses.
- **Hybrid search** — combining BM25 + dense retrieval into one result list.
- **RRF (Reciprocal Rank Fusion)** — merging ranked lists by **rank** (`1/(k+rank)`, k=60), not by score.
- **Reranking** — a second, accurate pass that re-orders retrieved candidates by relevance.
- **Bi-encoder vs cross-encoder** — bi-encoder embeds query/doc *separately* (fast, for retrieval);
  cross-encoder reads them *together* (accurate, for reranking).
- **VLM (Vision-Language Model)** — an LLM that can also "see" images and reason about them (read charts, scans, layouts).
- **Late interaction (ColPali)** — matching query tokens to document image *patches* at query time, instead of one vector each.

## Building with models
- **Agent** — a program that lets an LLM *take actions* in a loop: think → use a tool → see the
  result → repeat, until a task is done.
- **Tool / function calling** — giving an LLM the ability to call your functions (search, database,
  calculator) rather than only producing text.
- **API** — a way for your code to talk to a service over the web (e.g. send a prompt to OpenAI and
  get a reply).
- **SDK** — a ready-made library that wraps an API so you call simple Python functions instead of
  raw web requests.
- **Hugging Face** — a popular hub for downloading ready-made open models (the "app store" for AI
  models).
- **Fine-tuning** — further-training an existing model a little on your own data to change its
  style/behaviour. (Different from RAG, which adds *knowledge* at query time without retraining.)

## Agents & protocols (overview)
- **Agentic AI** — AI that doesn't just answer once but **takes actions in a loop** to finish a
  task (decide → act → check the result → repeat). An *agent* (above) is one such program.
- **ReAct loop** — the core agent pattern: **Reason** → **Act** (call a tool) → observe the result
  → repeat until the task is done.
- **Orchestration** — the code that coordinates the steps: which model/tool runs when, plus state,
  retries, and routing. The main framework is **LangGraph** (Phase 3).
- **Multi-agent system** — several specialised agents working together (e.g. a *supervisor* routing
  work to *worker* agents).
- **MCP (Model Context Protocol)** — an open standard (Anthropic, 2024) that lets an AI app connect
  to tools and data through **one universal adapter**, instead of hand-wiring every integration.
  Think "USB-C for AI tools." Deep dive in Phase 3.
- **A2A (Agent-to-Agent)** — an emerging standard for **different agents to talk to and collaborate
  with each other** (agent↔agent), vs MCP's agent↔tool. Awareness; worth tracking.

## Agentic build blocks (Phase 3 deep)
- **LangGraph** — the leading framework: build an agent as a **graph** of steps with shared state.
- **StateGraph / node / edge / state** — the graph (`StateGraph`), its steps (**nodes**), arrows
  (**edges**), and the shared data passed between them (**state**).
- **Reducer** — the rule for merging a node's update into state (overwrite · `add_messages` append ·
  `operator.add` concat). Plain field = overwrite; lists need a reducer.
- **Conditional edge** — a router that picks the next node from state — makes branches and loops.
- **Checkpointer** — saves state after every step (memory + crash-resume). `thread_id` = which
  conversation. **Store** = long-term, cross-session memory. Dev `MemorySaver`; prod `PostgresSaver`.
- **Tool / tool call / ToolMessage** — a function the LLM may use; the model emits a structured
  **call**, your code runs it, the result returns as a **ToolMessage**. **Function calling** = this
  mechanism, defined by a JSON-schema **tool contract**.
- **`create_react_agent`** — prebuilt ReAct loop. **Supervisor/worker** — coordinator routes to
  specialists. **`Command`** = route+update handoff; **`Send`** = parallel fan-out.
- **HITL (`interrupt`)** — pause the graph for human approval, then resume (needs a checkpointer).
- **CrewAI** — role-based **Crews** (autonomy) + **Flows** (event-driven control). **Sandbox** —
  isolated throwaway runtime (E2B/Docker) for running model-written code safely.
## LLMOps & production (Phase 4)
- **Eval metrics** — faithfulness (grounded?), answer relevancy, context precision/recall; tools
  **RAGAS** + **DeepEval** (pytest-style; **G-Eval** = LLM grades to your rubric).
- **LLM-as-a-judge** — use an LLM to grade outputs: **pointwise** (score one) / **pairwise** (A vs B);
  watch position/verbosity bias. **Observability** — trace every run (**LangSmith**; Phoenix/OTel).
- **Prompt injection** — input/doc tricks the model; defend with **Llama Guard**/**NeMo rails** + system-
  prompt isolation. **DLP** — detect/anonymise PII/PHI (**Presidio**). **Semantic cache** — reuse answers
  by meaning. **Circuit breaker/fallback** — retry → break → other provider (**LiteLLM router**).
- **Fine-tuning** — SFT (format), DPO (preference), **LoRA/QLoRA** (cheap adapters); after RAG, not before.
---
*If a term you hit isn't here, tell me and I'll add it.*
