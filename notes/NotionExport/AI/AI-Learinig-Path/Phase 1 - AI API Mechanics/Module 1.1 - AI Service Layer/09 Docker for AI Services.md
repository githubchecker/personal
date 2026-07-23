# 09 — Docker for AI Services

> Phase 1 · Module 1.1 · Lesson 9 · `[JD VERIFIED — 70%]`

## 🗺️ Stage 0 — Concept Map

To ship your AI service so it runs **identically** on any machine (your laptop, a server, the
cloud), you package it — code, Python, and dependencies — into a **Docker container**. It's named in
~70% of AI-backend JDs and is how you deploy the Phase 1 milestone. Builds on everything in Module
1.1 plus Phase 0.1 environments (lesson 02).

## 🔑 New Terms (plain English)

- **Image** — a frozen, packaged snapshot of your app + its dependencies (a blueprint).
- **Container** — a running instance of an image (the live process).
- **Dockerfile** — the recipe that builds the image, step by step.
- **Layer caching** — Docker reuses unchanged build steps, so rebuilds are fast.
- **`.dockerignore`** — a list of things to keep *out* of the image (`.venv`, `__pycache__`).
- **Multi-stage build** — a Dockerfile with a build stage + a slim final stage that ships only what's needed.
- **`docker-compose`** — run your service + its dependencies together locally from one YAML file.

## 🎈 Stage 1 — The Simple Idea (analogy: a shipping container)

Before standardized shipping containers, every cargo was loaded differently and broke in transit.
A **container** packs your app **with everything it needs** into one sealed box that runs the same
on any "ship" (host) or "port" (cloud). No more *"works on my machine."*

**The "Aha!":** the Dockerfile is a **repeatable recipe**; the image is the sealed box; the
container is that box **running**. Build once, run anywhere identically.

**💢 The old/painful way ("works on my machine")** — deploying means manually matching the Python
version, OS libraries, and exact dependency versions on every server — and it still breaks when one
host differs. A container ships all of that *inside* the image.

## ⚙️ Stage 2 — How It Actually Works

### 9.1 The Dockerfile (current FastAPI pattern)

```dockerfile
FROM python:3.12-slim                 # start from an official slim Python image

WORKDIR /code

# Copy ONLY requirements first — so the slow "pip install" layer is cached and
# reused on every code change (huge speed-up).
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the app code LAST (it changes most often → only this layer rebuilds).
COPY ./app /code/app

# Exec form (JSON array) — required so the app shuts down gracefully and
# lifespan startup/shutdown (lesson 07) runs.
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

**Which base image? (a real 3-way choice).** A *wheel* is a pre-built Python package; some only ship
for one flavour of the system's core C library (*glibc* vs *musl*).

- **`python:3.12-slim`** (glibc-based) — the **right default**.
  - **Key features:** small, but glibc-based so Python/ML wheels install cleanly.
  - **✅ Use when:** almost always — especially anything with ML/data dependencies.
  - **🚫 Avoid when → use distroless:** you need the most locked-down image for security.
  - **⚠️ Gotcha:** still has a shell and package manager, so it's not the smallest possible.
- **`alpine`** (musl-based) — smallest, but risky for AI.
  - **Key features:** a tiny base image.
  - **✅ Use when:** a pure-Python service where image size is the top priority.
  - **🚫 Avoid when → use slim:** any ML/data deps — musl breaks many wheels and forces slow source builds.
  - **⚠️ Gotcha:** "it's smaller" often costs hours of broken-wheel debugging — usually **avoid for AI**.
- **distroless** — no shell, minimal contents.
  - **Key features:** smallest *attack surface* (the least stuff that could be exploited); no shell inside.
  - **✅ Use when:** security/compliance wants a minimal image and you don't need to shell in to debug.
  - **🚫 Avoid when → use slim:** you're still iterating and want to `docker exec` a shell to debug.
  - **⚠️ Gotcha:** no shell makes debugging harder — pair it with good logging.

**Rule: stay on `slim` unless you have a specific reason.**

### 9.2 Multi-stage builds — smaller, safer images

If your deps need **compilers** (some ML libs) or you want the **smallest** final image, use a
**multi-stage** build: install in a *builder* stage, then copy only the finished packages into a
clean final stage (no compilers/build junk shipped):

```dockerfile
# ---- stage 1: build ----
FROM python:3.12 AS builder
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt   # install into a folder

# ---- stage 2: final (slim) ----
FROM python:3.12-slim
WORKDIR /code
COPY --from=builder /deps /usr/local/lib/python3.12/site-packages   # copy ONLY the packages
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

**Single-stage vs multi-stage (pick one):**
- **Single-stage** (one `FROM`, as in 9.1)
  - **✅ Use when:** a simple pure-Python service with no compiled dependencies.
  - **🚫 Avoid when → use multi-stage:** deps need compilers, or you want the smallest/safest final image.
  - **⚠️ Gotcha:** build tools and caches end up *in* the shipped image, making it bigger.
- **Multi-stage** (a builder stage + a slim final stage)
  - **✅ Use when:** deps need build tools (some ML libs), or image size / attack surface matters.
  - **🚫 Avoid when → use single-stage:** a trivial service — the extra stage is needless complexity.
  - **⚠️ Gotcha:** you must copy the *right* paths from the builder (the installed packages), or it breaks at run time.

### 9.3 `.dockerignore` (keep junk out)

```
.venv
__pycache__
*.pyc
.env
.git
```

### 9.4 Build & run

```powershell
docker build -t my-ai-service .
docker run -p 8000:80 --env-file .env my-ai-service   # pass secrets in, don't bake them in
```

### 9.5 `docker-compose` — run the service + its deps locally `[awareness]`

When your service needs **companions** (later: a vector DB, Redis), `docker-compose` starts them all
with one command from a YAML file:

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:80"]
    env_file: .env
  # redis:  ...        # add dependencies here (Phase 2+)
```
```powershell
docker compose up        # builds + runs everything together
```

### 9.6 The AI-specific catch: memory × workers

Each **worker process** loads its **own copy** of your model into RAM. With `fastapi run --workers
4` and a **1 GB** model, that's **~4 GB** RAM. So:
- For a cluster (Kubernetes/Container Apps), prefer **one process per container** and scale by adding
  **containers**, not workers.
- Use `--workers` only on a single box, and **size memory to model × workers** or you'll hit
  out-of-memory crashes.
- (The old `tiangolo/uvicorn-gunicorn-fastapi` base image is **deprecated** — build from the plain
  Python image as above.)

### 9.7 A health check

```python
@app.get("/health")
def health():
    return {"status": "ok"}            # orchestrators (e.g. Kubernetes) ping this to know it's alive
```

> 🔬 **Under the hood:** each Dockerfile instruction creates a cached, read-only **layer**; the image
> is a stack of those layers, so a rebuild only re-runs layers *after* the first change (that's why
> `requirements.txt` is copied before the code). A **container** is that image plus a thin writable
> layer, running your `CMD` as the main process (**PID 1**) in its own isolated space (a *namespace*).

## 🚀 Stage 3 — In Practice / Why It Matters

You'll containerize the Phase 1 gateway and deploy it (e.g. Azure Container Apps). The Dockerfile
ordering trick keeps builds fast; the memory×workers rule decides how many **replicas** (copies of
the container) fit per machine — *the* sizing question for model-serving services.

## ⚖️ Variations & When to Use

| Decision | Options | Use which |
| --- | --- | --- |
| **Base image** | `slim` vs `alpine` vs `distroless` | **`slim`** default (ML wheels work) · `alpine` only for smallest-at-all-costs (musl breaks wheels) · distroless for minimal attack surface |
| **Build** | single-stage vs **multi-stage** | single-stage for simple pure-Python · **multi-stage** when deps need compilers or image size/security matters |
| **Scale** | `--workers` vs more containers | `--workers` on a single box (mind model×memory) · **more containers** on a cluster (one process each) |
| **Run multiple services** | `docker run` vs `docker compose` | `docker run` for the single service · **compose** when you need companions (DB/cache) locally |

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| Every build re-installs all deps (slow) | Copied code before `requirements.txt` | Copy `requirements.txt` + `pip install` **before** the code |
| Image is huge / leaks `.venv` or `.env` | No `.dockerignore` | Add `.dockerignore` (exclude `.venv`, `.env`, `.git`) |
| App doesn't stop cleanly / lifespan skipped | Shell-form `CMD` | Use **exec form**: `CMD ["fastapi","run",...]` |
| Container `OOMKilled` | workers × model size > RAM | Fewer workers, or one process per container + more containers |
| Secrets baked into the image | `COPY .env` / hardcoded | Pass at run time: `--env-file .env` (and `.dockerignore` it) |

## 📌 Quick Reference

```dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt   # cached layer
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]      # exec form
```
```powershell
docker build -t my-ai-service .
docker run -p 8000:80 --env-file .env my-ai-service
```
- **requirements before code** (caching) · **exec-form CMD** · **`.dockerignore`** · **memory = model × workers** · **multi-stage** for smaller images.

> 🎯 **Interview angle:** "Why copy `requirements.txt` before the app code in a Dockerfile?" →
> layer caching: dependencies change rarely, so that slow `pip install` layer is reused; only the
> fast code-copy layer rebuilds when you change code.

## 🛑 STOP — Self-Check

Your model is **1 GB** and you set `--workers 4` in a container with **3 GB** RAM. What happens, and
what are two ways to fix it?

<details><summary>Answer</summary>

It **crashes (out-of-memory / `OOMKilled`)**: each of the 4 workers loads its **own** 1 GB copy of
the model = **~4 GB**, exceeding the 3 GB limit. Fixes: (1) **reduce workers** (e.g. 1–2) so
model×workers fits in RAM; or (2) run **one process per container** and scale by adding **more
containers** (the cluster handles replication), giving each container enough memory for a single
model copy.
</details>
