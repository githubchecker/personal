# 02 — Custom Vision (Train Your Own Image Models)

> Phase 5 · Module 5.4 · Lesson 2 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 Computer Vision (10–15%)**
> *"Implement custom vision models" is an explicit exam objective — the answer whenever prebuilt Vision can't
> recognise *your* categories.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Prebuilt Vision (Lesson 01) knows *generic* things — "car", "person", "text". It has no
idea about **your** categories: your 5 product lines, your specific defect types, your brand's logos. **Custom
Vision** fixes that: you **label** example images and **train** a small model that recognises *your* classes.
The exam tests choosing classification vs detection, labelling, training, evaluating, publishing, and consuming.
*(Video is its own lesson — 4.3.)*

**Why care:** it's a named exam objective and the standard move for any proprietary visual recognition task.

## 🔑 New Terms (plain English)
- **Image classification** — "which **category** is this whole image?" (one or more labels per image).
- **Object detection** — "**where** are the items?" (labels **plus bounding boxes**).
- **Labelling** — tagging your example images so the model can learn.
- **Training / iteration** — building a model version from your labelled data.
- **Precision / recall / mAP** — evaluation metrics (correctness, completeness, detection quality).
- **Publish / consume** — make the trained model callable, then call it from an app.
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: training a new hire on your products)
A new hire doesn't know your products. You show them **labelled photos** — "this is Model A, this is a cracked
casing" — until they can spot them on sight. **Custom Vision** is that training: your labels teach a small model
*your* categories. **Aha!:** prebuilt = generic knowledge out of the box; custom = your labels create your own
recogniser.

## ⚙️ Stage 2 — How It Works (the workflow, each step a mini-reference)

#### Choose classification vs object detection (a real choice)
- **Classification** — "what category is this image?" **✅ Use when:** one label per image (defective vs ok). **🚫
  Avoid → detection:** when you need *where*. **Object detection** — "what items and where?" **✅ Use when:** count
  or locate items (boxes). **⚠️:** detection needs more labelling effort (draw boxes).

#### Label images
- **What & why:** tag each training image (and draw boxes for detection). **✅ Use when:** building any custom
  model. **⚠️ Gotcha:** you need **enough** balanced examples per class, or the model is weak/biased.

#### Train & evaluate (precision / recall / mAP)
- **What & why:** train an iteration, then read **precision** (of what it flagged, how much was right),
  **recall** (of what it should find, how much it found), and **mAP** (detection quality). **✅ Use when:**
  deciding if it's good enough. **⚠️:** low scores usually mean *more/cleaner data*, not more training.

#### Publish & consume (incl. code-first)
- **What & why:** publish the trained iteration to get an endpoint, then call it from an app via SDK/REST. You
  can also build models **code-first**. **✅ Use when:** putting it into production. **⚠️:** version your iterations; test before swapping.

> 🔬 **Under the hood:** Custom Vision trains a compact image model on **your labels** (transfer learning on a
> pretrained backbone), so it works with relatively few images. The metrics tell you whether you need more or
> better-balanced data before publishing.

### 💻 The SDK in code
Custom Vision has **two** clients backed by **two** resources/keys: **Training** and **Prediction**.
```python
# pip install azure-cognitiveservices-vision-customvision
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

# --- TRAIN (Training resource/key) ---
train_cred = ApiKeyCredentials(in_headers={"Training-key": "<training-key>"})
trainer = CustomVisionTrainingClient("https://<resource>.cognitiveservices.azure.com/", train_cred)

project  = trainer.create_project("defects")          # pick a classification/detection DOMAIN
crack    = trainer.create_tag(project.id, "cracked")  # a label/tag
# trainer.create_images_from_files(project.id, ...)   # upload + tag your images
iteration = trainer.train_project(project.id)         # train an ITERATION
trainer.publish_iteration(project.id, iteration.id, "model1", "<prediction-resource-id>")

# --- PREDICT (Prediction resource/key) ---
pred_cred = ApiKeyCredentials(in_headers={"Prediction-key": "<prediction-key>"})
predictor = CustomVisionPredictionClient("https://<resource>.cognitiveservices.azure.com/", pred_cred)
results = predictor.classify_image(project.id, "model1", open("part.jpg", "rb").read())
for p in results.predictions:
    print(p.tag_name, p.probability)                  # 'cracked' 0.93
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `azure-cognitiveservices-vision-customvision` |
| Two resources | **Training** (key) + **Prediction** (key) — separate |
| Clients | `CustomVisionTrainingClient` · `CustomVisionPredictionClient` |
| Train flow | `create_project` → `create_tag` → upload images → `train_project` → `publish_iteration` |
| Predict | `classify_image` / `detect_image` (+ `_url`, `_with_no_store`) → `.predictions[].tag_name/.probability` |
| Project types | **Classification** (multiclass/multilabel) · **Object detection** |
| Domains | General · Food · Landmarks · Retail · **Compact** (edge export) |
| Export (Compact) | ONNX · TensorFlow · CoreML · Docker |
| Metrics | precision · recall · **mAP** (detection) |

### 🎯 Exam facts to memorise
- **Two resources/keys:** a **Training** resource and a **Prediction** resource (don't mix the keys).
- **Publish an iteration** before you can call it for prediction; predict by the **published model name**.
- **Compact domains** are what make a model **exportable to the edge** (ONNX/TensorFlow/CoreML/Docker).
- **Classification** = label(s) per image; **Object detection** = labels **+ bounding boxes** (and counts).
- Evaluation: **precision** (of what it flagged) · **recall** (of what it should find) · **mAP** (detection quality).
- Low scores usually mean **more / better-balanced labelled data**, not more training cycles.

## 🚀 Stage 3 — In Practice / Why It Matters
A manufacturer trains **object detection** to locate defects on a production line; a retailer trains
**classification** to sort product photos. Both label → train → check precision/recall → publish → consume. On
the exam: "which category" → classification; "what and where / count" → detection; "metrics low" → more/better
data; "generic objects" → prebuilt Vision (Lesson 01).

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Which category is this image? | **classification** |
| What items, and where/how many? | **object detection** |
| Generic objects/text | **AI Vision** prebuilt (Lesson 01) |
| Video content/movement | **Video Indexer / Spatial Analysis** (Lesson 03) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Weak/biased model | too few / imbalanced images | add more, balanced labelled examples |
| Need locations, only got labels | used classification | use **object detection** |
| Overkill for generic objects | trained custom unnecessarily | use prebuilt **AI Vision** |
| Prod broke after retrain | swapped iteration untested | evaluate the new iteration first |

## 📌 Quick Reference
- **Classification = which category · Object detection = what + where (boxes).**
- Workflow: **label → train → evaluate (precision/recall/mAP) → publish → consume.**
- Low metrics → more/cleaner balanced data. Generic → prebuilt Vision; video → Lesson 03.

## 🎯 Exam-style practice
**Q1.** Your model must run **offline on a handheld scanner**. What must you choose at project creation, and which export format?
<details><summary>Answer</summary>A **Compact** domain (so the model is exportable), then export to **ONNX / TensorFlow / CoreML / Docker** for the edge device.</details>

**Q2.** Prediction calls fail auth even though training worked. Likely cause?
<details><summary>Answer</summary>You used the **Training key** for prediction. Custom Vision has **two resources** — use the **Prediction key/endpoint** with `CustomVisionPredictionClient`.</details>

**Q3.** You must **count** scratches on each part. Classification or detection, and which metric matters?
<details><summary>Answer</summary>**Object detection** (boxes give location + count); judge it with **mAP** (plus precision/recall).</details>

## 🛑 STOP — Self-Check
A factory wants to (a) decide if each part photo is **"pass" or "fail"**, and (b) **locate and count every
scratch** on a part. Which Custom Vision model type for each — and what do you check before publishing?

<details><summary>Answer</summary>

- **(a) Pass/fail per image → image classification** (one label per image).
- **(b) Locate & count scratches → object detection** (labels **+ bounding boxes**, so you get position and count).
- **Before publishing:** check **precision/recall** (and **mAP** for the detector) on a test set; if low, add
  **more, balanced labelled images** rather than just retraining. Then publish and consume from the app.
</details>

⏭️ **Next:** 03 — Video Analysis (Branch 4.3).
