# 01 — Analyze Images & Extract Text (OCR)

> Phase 5 · Module 5.4 · Lesson 1 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Computer Vision (10–15%)**
> *"Analyze images" and OCR are bread-and-butter exam questions and the most common prebuilt-vision task in
> real Azure projects.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** You have images — product photos, scanned documents, receipts, signs — and you need a
machine to **see** them: tag what's in them, find objects, caption them, and **read the text** (printed *and*
handwritten). Azure AI Vision does all this **prebuilt** (no training): you call an endpoint and get back
structured results. Reach for custom training only when your categories are unique (Lesson 02).

**Why care:** image analysis + OCR ("Read") are explicit exam objectives and the default first tool for any vision task.

## 🔑 New Terms (plain English)
- **Visual features** — the things Vision can return: tags, objects, a caption, people, smart-crops.
- **Read (OCR)** — the API that extracts **printed and handwritten** text from images/PDFs, with positions.
- **Bounding box** — the rectangle coordinates locating a detected object or line of text.
- **Confidence** — a 0–1 score for how sure the model is.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a sharp-eyed assistant)
Hand a photo to a quick, sharp-eyed assistant: they instantly tell you *what's in it* ("a person, a car, a stop
sign"), *where* each thing is, *a one-line caption*, and they **read aloud any text** on it — even messy
handwriting. **Aha!:** prebuilt vision = call an endpoint, get answers; no training, no labelling.

## ⚙️ Stage 2 — How It Works (each a mini-reference, with the SDK)

**One client, one call.** Azure AI Vision 4.0 is the `ImageAnalysisClient`: you pass the image plus a list of
`VisualFeatures`, and read **typed** results back (no raw-JSON wrangling).

```python
# pip install azure-ai-vision-imageanalysis
from azure.ai.vision.imageanalysis import ImageAnalysisClient        # the Vision 4.0 client
from azure.ai.vision.imageanalysis.models import VisualFeatures      # the feature enum
from azure.core.credentials import AzureKeyCredential               # key auth (dev only)
# from azure.identity import DefaultAzureCredential                 # Entra ID (prod) — no key to leak

client = ImageAnalysisClient(
    endpoint="https://<your-resource>.cognitiveservices.azure.com/",  # the resource's DEFAULT endpoint
    credential=AzureKeyCredential("<key>"),                            # or DefaultAzureCredential()
)

result = client.analyze(
    image_data=open("parcel.jpg", "rb").read(),   # raw bytes; OR image_url="https://..."
    visual_features=[                              # ask ONLY for what you need (cost + latency)
        VisualFeatures.CAPTION,                    # one-line description of the whole image
        VisualFeatures.READ,                       # OCR: printed AND handwritten text
        VisualFeatures.TAGS,                       # content labels for the whole image
        VisualFeatures.OBJECTS,                    # located objects + bounding boxes
    ],
    gender_neutral_caption=True,                   # say "person" not "man/woman"
    language="en",                                 # caption/tags language
)

print(result.caption.text, result.caption.confidence)   # e.g. "a parcel on a doorstep" 0.86
for block in result.read.blocks:                         # OCR is blocks → lines → words
    for line in block.lines:
        print(line.text)                                 # a whole line of text
        for word in line.words:
            print(word.text, word.confidence)            # each word + its 0–1 confidence
```

#### Select visual features — `VisualFeatures` (a real choice)
- **What & why:** the enum that drives the request: `TAGS`, `OBJECTS`, `CAPTION`, `DENSE_CAPTIONS`, `PEOPLE`,
  `SMART_CROPS`, `READ`. **✅ Use when:** generic scene understanding / OCR. **⚠️ Gotcha:** `CAPTION` /
  `DENSE_CAPTIONS` are offered only in **select regions** — request them elsewhere and the call errors.

#### Detect objects & generate tags — `VisualFeatures.OBJECTS` / `TAGS`
- **What & why:** `result.tags.list` (whole-image labels) and `result.objects.list` (each with `.tags` +
  `.bounding_box`). **✅ Use when:** "what's in this image / where?" for **generic** categories. **🚫 Avoid →
  Custom Vision:** for your own categories (Lesson 02).

#### Extract printed + handwritten text — `VisualFeatures.READ` (OCR)
- **What & why:** Read 4.0 returns **`result.read.blocks → lines → words`**, each with `.text`, **`.confidence`**,
  and a **`.bounding_polygon`** — handling **printed *and* handwritten in one feature** (there is no separate
  handwriting call). **✅ Use when:** digitising signs, labels, notes, whiteboards. **🚫 Avoid → Document
  Intelligence:** when you need *form fields/structure* or **multi-page PDFs** (`prebuilt-read`). **⚠️:** image quality drives accuracy.

#### Interpret responses — confidence + bounding boxes
- **What & why:** every result carries a **confidence (0–1)** and, where located, a **bounding box/polygon**.
  **✅ Use when:** filtering weak detections. **⚠️:** threshold on confidence before you act on a result.

> 🔬 **Under the hood:** one **Azure AI Vision** resource; the SDK call is
> `POST {endpoint}/computervision/imageanalysis:analyze?features=caption,read&api-version=2024-02-01`. These are
> **prebuilt** models — no training; you send the image and parse the typed result.

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `azure-ai-vision-imageanalysis` |
| Client | `ImageAnalysisClient(endpoint, credential)` |
| Call | `client.analyze(image_data=… \| image_url=…, visual_features=[…])` |
| Feature enum | `VisualFeatures.{TAGS, OBJECTS, CAPTION, DENSE_CAPTIONS, PEOPLE, SMART_CROPS, READ}` |
| OCR result path | `result.read.blocks[].lines[].words[]` → `.text`, `.confidence`, `.bounding_polygon` |
| Objects/tags | `result.objects.list[].bounding_box` / `result.tags.list[]` |
| Auth | `AzureKeyCredential(key)` (dev) · `DefaultAzureCredential()` (prod) |
| REST | `imageanalysis:analyze?api-version=2024-02-01&features=caption,read` |

### 🎯 Exam facts to memorise
- **Vision 4.0 features:** caption, dense captions, tags, objects, people, smart crops, **read (OCR)**.
- **`READ` does printed *and* handwritten** in one feature — no separate handwriting API.
- **Caption / dense captions are region-limited** (GA in select regions only).
- **Smart crops** = thumbnails focused on the region of interest (you can request aspect ratios).
- Multi-page docs / text **with layout & tables** → **Document Intelligence `prebuilt-read` / `prebuilt-layout`**, not Image Analysis.
- (Check current docs for exact input size/dimension limits before quoting them.)

## 🚀 Stage 3 — In Practice / Why It Matters
Prebuilt Vision handles a huge share of real tasks: auto-tagging a media library, reading text off delivery
labels, captioning images for accessibility, digitising handwritten forms. On the exam, "read text" → **Read
(OCR)**; "what's in the image" → **analyze/tags/objects**; "our own categories" → **Custom Vision**; "form
fields" → **Document Intelligence**.

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Tags / objects / caption (generic) | **AI Vision analyze** |
| Read printed text | **AI Vision Read (OCR)** |
| Read handwriting | **AI Vision Read** |
| Your own image categories | **Custom Vision** (Lesson 02) |
| Fields from a form/invoice | **Document Intelligence** (5.6) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Need form fields, used OCR | wrong tool | use **Document Intelligence** |
| Need own categories, used Vision | generic only | train **Custom Vision** |
| Acting on bad detections | ignored confidence | threshold on confidence |
| Poor OCR | low image quality | improve resolution/contrast |

## 📌 Quick Reference
- **Analyze** = tags/objects/caption (generic). **Read** = printed **and** handwritten text + positions.
- Confidence + bounding boxes in the JSON — threshold them. Prebuilt = no training.
- Own categories → Custom Vision; form fields → Document Intelligence.

## 🎯 Exam-style practice
**Q1.** Your code calls `client.analyze(...)` and must return both a one-line description *and* any text in the
image in a **single** request. Which `visual_features` do you pass?
<details><summary>Answer</summary>`[VisualFeatures.CAPTION, VisualFeatures.READ]` — one `analyze` call can request multiple features at once.</details>

**Q2.** A 30-page **scanned PDF contract** must have its text extracted **with layout and tables preserved**.
Image Analysis `READ`, or Document Intelligence?
<details><summary>Answer</summary>**Document Intelligence** (`prebuilt-read` for text, `prebuilt-layout` for tables/structure). Image Analysis works on a single image and returns text without document layout.</details>

**Q3.** The app must **not act on uncertain detections**. Which result property do you threshold, and what is its range?
<details><summary>Answer</summary>`.confidence` on each result (caption/word/object), range **0–1**. Discard results below your chosen threshold.</details>

## 🛑 STOP — Self-Check
A courier app must (a) **read the printed address and the customer's handwritten signature line** off a parcel
photo, and (b) flag if a **generic "package" object** is present. Which Vision capabilities — and what do you
check on each result?

<details><summary>Answer</summary>

- **(a) Address + handwriting → Azure AI Vision Read (OCR)** — it extracts **printed *and* handwritten** text
  with positions.
- **(b) Detect a package → object detection / tags** (generic categories).
- **Check the confidence score** on each result (and bounding boxes for location), thresholding so you don't act
  on weak detections. (If the courier had *its own* package types, that'd be **Custom Vision** instead.)
</details>

⏭️ **Next:** 02 — Custom Vision (Branch 4.2).
