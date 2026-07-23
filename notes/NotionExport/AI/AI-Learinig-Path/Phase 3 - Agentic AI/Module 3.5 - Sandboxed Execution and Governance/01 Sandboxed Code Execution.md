# 01 — Sandboxed Code Execution (E2B & Docker)

> Phase 3 · Module 3.5 · Lesson 1 · `[OPTIONAL — 🟢 awareness; build only for code/data-analysis agents]`

> ⚠️ **Awareness.** Know *why* agents need a sandbox and the two options. Your Docker knowledge applies.

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** A code-exec tool lets the agent run **model-written code** — terrifying without
isolation (delete files, exfiltrate data, mine crypto). A **sandbox** runs it in a locked, throwaway box.
Two options: **E2B** (managed cloud sandbox) and **Docker** (your own isolated container).

## 🔑 New Terms
**Sandbox** — isolated throwaway runtime. **E2B** — managed sandbox SDK. **Docker isolation** — `--network
none`, `--cap-drop ALL`, `--read-only`, memory cap. ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Idea: let the intern code in a sealed room with no exit — they work, you keep the output, burn the room. **Aha!:** isolate + dispose.

## ⚙️ Stage 2 — the two ways to sandbox (each a mini-reference)
#### E2B — managed cloud sandbox
- **What & why:** a hosted SDK that spins up a fresh isolated box per run: `Sandbox().run_code(code)`. **✅ Use
  when:** you want speed and no infra to manage. **🚫 Avoid → Docker:** on-prem-only or no third parties. **⚠️
  Gotcha:** per-run cost + a third-party dependency.
#### Docker isolation — your own container
- **What & why:** run code in a locked, throwaway container: `docker run --rm --network none --cap-drop ALL
  --read-only -m 512m`. **✅ Use when:** self-hosting; you already know Docker. **🚫 Avoid → E2B:** when you
  want zero infra. **⚠️:** you own the lockdown — drop caps, no network, cap memory and time.
Either way: always cap time/memory and cut the network; the box is disposable.

> 🔬 Both are ephemeral isolated runtimes; **never** `exec()` model-written code in your own process — that's host-level access.

## ⚖️ E2B = quick/managed · Docker = control/on-prem. 🐛 no isolation→breach; no caps→runaway. 📌 sandbox + dispose; E2B managed / Docker self-host; drop caps, no net, cap mem+time.
## 🛑 Why never run model code in your process? <details><summary>A</summary>It gets full host access — can delete files or exfiltrate data. Use a sandbox (E2B/Docker) with dropped privileges, no network, and time/memory caps.</details>

⏭️ **Next:** 02 — Human-in-the-Loop.
