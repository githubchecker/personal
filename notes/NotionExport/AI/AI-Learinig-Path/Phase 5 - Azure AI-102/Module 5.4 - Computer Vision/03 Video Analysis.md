# 03 — Video Analysis (Video Indexer & Spatial Analysis)

> Phase 5 · Module 5.4 · Lesson 3 · **Importance: 🟡 SHOULD KNOW · `[JD VERIFIED]` · AI-102 Computer Vision (10–15%)**
> *"Analyze videos" is a named exam objective; video insight and people-movement analytics show up in retail,
> security, and media AI roles.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Images are one frame; **video** is thousands of frames plus audio. Two different needs:
understand the *content* of a video (what's said, who appears, what topics) → **Azure AI Video Indexer**; and
track the *movement of people* in a live or recorded stream (how many entered, where they queued) → **Spatial
Analysis**. The exam tests choosing and using each.

**Why care:** it's an explicit exam objective, and video analytics is a high-value real-world Azure AI use case.

## 🔑 New Terms (plain English)
- **Azure AI Video Indexer** — extracts insights from video/audio: transcription, faces, topics, labels,
  sentiment, OCR-on-frames, chapters.
- **Spatial Analysis** — a Vision capability that detects **presence and movement of people** in video (counts,
  zones, lines crossed).
- **Insight / timeline** — the structured, time-stamped results Video Indexer returns.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: two different specialists watching a CCTV feed)
One specialist is a **note-taker** who watches the whole video and writes a rich, time-stamped summary —
"speaker said X at 02:13, logo appears at 04:00, topic is returns" (**Video Indexer**). The other is a
**counter** standing at the door tallying how many people walk in and which way they go (**Spatial Analysis**).
**Aha!:** one understands *content*, the other measures *people movement* — different jobs, different tools.

## ⚙️ Stage 2 — How It Works (each a mini-reference)

#### Azure AI Video Indexer
- **What & why:** upload a video (or point at a live stream) and get a timeline of **transcription, speakers,
  faces, topics, labels, keyframes, OCR text, sentiment, and chapters** — searchable and exportable.
- **✅ Use when:** media archives, meeting/recording search, content moderation, accessibility (captions). **🚫
  Avoid → Spatial Analysis:** when you only need people counts/movement. **⚠️ Gotcha:** face features have
  responsible-AI/usage constraints; review policy before enabling.

#### Spatial Analysis (Azure AI Vision)
- **What & why:** processes camera/video to detect **people presence and movement** — count people in a zone,
  count line crossings (entries/exits), measure dwell time/distance.
- **✅ Use when:** retail footfall, queue management, occupancy, safety distancing. **🚫 Avoid → Video Indexer:**
  when you need transcript/topics, not movement. **⚠️:** runs near the edge for live streams; mind privacy/consent.

> 🔬 **Under the hood:** Video Indexer runs many models (speech-to-text, face, OCR, label) across frames + audio
> and stitches them into one time-indexed JSON. Spatial Analysis runs person-detection + tracking on the video
> stream and emits events (e.g. "person crossed line A") you aggregate into counts.

### 💻 The API in practice
Both are **API / portal / container**-driven rather than one tidy Python SDK:
- **Video Indexer** — upload and read insights via its **REST API**: get an **access token**, then
  `POST .../Accounts/{accountId}/Videos?name=...&videoUrl=...&accessToken=...`; poll for the indexed **insights
  JSON** (transcript, faces, topics, labels, OCR, keyframes). Also fully usable from the **Video Indexer portal**.
- **Spatial Analysis** — runs as an **Azure AI Vision container** at the edge; you configure **operations**
  (e.g. *count people in a zone*, *count line crossings*) with **zones/lines** on the camera view; it emits **events**.

> 🔎 Honesty note: Video Indexer is primarily **REST + portal** (no first-class Python SDK), and Spatial Analysis
> is **container + config** — memorise the *workflow and operations*, not SDK class names.

### 📦 API quick reference
| Thing | Value |
|---|---|
| Video Indexer | REST API + portal; needs **account ID** + **access token** |
| VI upload | `POST /Accounts/{id}/Videos?name=...&videoUrl=...&accessToken=...` |
| VI insights | transcript · speakers · faces · topics · labels · OCR · keyframes · sentiment · chapters |
| Spatial Analysis | Azure AI Vision **container** (edge) |
| SA operations | people **count in zone** · **line crossing** (entries/exits) · dwell/distance |

### 🎯 Exam facts to memorise
- **Content insight (transcript/faces/topics/search)** → **Video Indexer**; **people movement/counts** → **Spatial Analysis**.
- Video Indexer is **REST + portal** (access token + account ID); returns one **time-indexed insights JSON**.
- Spatial Analysis runs in a **container at the edge**, configured with **zones/lines + operations**, emitting events.
- **Face**-related insights carry **Limited Access / responsible-AI** requirements — review policy before enabling.

## 🚀 Stage 3 — In Practice / Why It Matters
A media company uses **Video Indexer** to auto-caption and make its archive searchable; a retailer uses
**Spatial Analysis** to count footfall and queue lengths in real time. Both are "analyze videos" on the exam —
the deciding question is *content insight* (Indexer) vs *people movement* (Spatial).

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Transcript, topics, faces, search of a video | **Video Indexer** |
| Count people / movement / zones in a stream | **Spatial Analysis** |
| Text/objects in a single image | **Azure AI Vision** (Lesson 01) |
| Your own image categories | **Custom Vision** (Lesson 02) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Need footfall counts, used Video Indexer | wrong tool | use **Spatial Analysis** (people movement) |
| Need transcript, used Spatial Analysis | wrong tool | use **Video Indexer** (content insights) |
| Face insights blocked | responsible-AI policy | review face usage policy/limited-access requirements |

## 📌 Quick Reference
- **Content insight (transcript/faces/topics) → Video Indexer.**
- **People movement/counts → Spatial Analysis.**
- Single image → AI Vision; your own categories → Custom Vision.

## 🎯 Exam-style practice
**Q1.** You must **search recorded lectures for every mention of a topic**. Which service, and what does it return?
<details><summary>Answer</summary>**Video Indexer** — it transcribes and indexes topics, returning a **time-indexed insights JSON** you can search.</details>

**Q2.** You must **count entries through a doorway** from a live camera, on-prem. Which service, and how is it deployed?
<details><summary>Answer</summary>**Spatial Analysis** — an Azure AI Vision **container** at the edge, configured with a **line-crossing** operation.</details>

**Q3.** Enabling **face** insights is blocked. Why?
<details><summary>Answer</summary>Face features are under **Limited Access / responsible-AI** controls; you must meet the usage requirements first.</details>

## 🛑 STOP — Self-Check
A supermarket wants (a) to **count how many shoppers enter each hour and how long the checkout queue is**, and
(b) to **search its training videos for every clip where "food safety" is discussed**. Which service for each?

<details><summary>Answer</summary>

- **(a) Footfall + queue length → Spatial Analysis** — it detects **people presence and movement** (entries,
  zone occupancy, dwell/queue time) in the camera stream.
- **(b) Search videos for a spoken topic → Azure AI Video Indexer** — it **transcribes** and indexes topics, so
  you can search the timeline for "food safety" mentions.

Movement = Spatial Analysis; content/transcript = Video Indexer.
</details>

⏭️ **Next:** Module 5.5 — NLP & Speech (Branch 5.1).
