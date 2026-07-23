# 02 — Azure AI Speech

> Phase 5 · Module 5.5 · Lesson 2 · **Importance: 🔴 MUST KNOW · `[JD VERIFIED]` · AI-102 NLP (15–20%)**
> *"Process and translate speech" is an explicit exam objective; voice interfaces and call-centre AI make Speech a common JD requirement.*

---

## 🗺️ Stage 0 — Concept Map
**The problem first.** Text isn't the only channel — apps need to **listen** (transcribe calls/commands),
**speak** (read answers aloud), sound **natural** (control delivery), handle **your jargon/accents**, react to
**wake-words/commands**, and **translate speech** live. **Azure AI Speech** covers all of it.

**Why care:** explicit exam objective; voice + call-analytics are high-value real-world Azure use cases.

## 🔑 New Terms (plain English)
- **STT (speech-to-text)** — transcribe spoken audio into text.
- **TTS (text-to-speech)** — synthesise spoken audio from text (neural voices).
- **SSML** — Speech Synthesis Markup Language: XML to control pronunciation, pitch, pace, pauses, and voice.
- **Custom speech** — train recognition on **your** audio/jargon/accents.
- **Keyword / intent recognition** — wake-words ("Hey…") and command intents from speech.
- **Speech translation** — translate spoken input to another language (speech-to-text or speech-to-speech).
  ([glossary](../../AI%20Terms%20-%20Plain%20English%20Glossary.md))

## 🎈 Stage 1 — Simple Idea (analogy: a bilingual transcriber + voice actor)
Picture one assistant who **types what they hear** (STT), **reads text aloud** in a natural voice (TTS), follows
**stage directions** for delivery (SSML), can be **coached on your industry jargon** (custom speech), perks up at
a **wake-word** (keyword), and **interprets live across languages** (speech translation). **Aha!:** prebuilt voices
work out of the box; SSML directs *how* it speaks; custom speech adapts *what* it understands.

## ⚙️ Stage 2 — How It Works (each capability a mini-reference)

#### Speech-to-text (STT)
- **What & why:** transcribe audio (live or files) to text. **✅ Use when:** call transcription, dictation, voice commands. **⚠️ Gotcha:** noise/accents/jargon lower accuracy → consider custom speech.

#### Text-to-speech (TTS) + generative speaking
- **What & why:** synthesise natural neural voices; integrate generative speaking into apps. **✅ Use when:** spoken responses, IVR, accessibility. **⚠️:** pick an appropriate voice/locale.

#### SSML (control delivery)
- **What & why:** XML around text to set **pronunciation, pitch, rate, pauses, emphasis, and voice**. **✅ Use when:**
  fixing a mispronounced brand name or flat delivery. **🚫 Avoid → retraining first:** markup is cheaper than custom voice. **⚠️:** malformed SSML is ignored/errored.

#### Custom speech
- **What & why:** train STT on **your** audio + vocabulary (product names, accents, domain terms). **✅ Use when:**
  generic STT keeps mishearing your jargon. **🚫 Avoid → generic STT:** when accuracy is already fine. **⚠️:** needs representative audio/transcripts.

#### Keyword & intent recognition
- **What & why:** detect **wake-words** and recognise spoken **intents/commands** (often with CLU). **✅ Use when:**
  hands-free / voice-command apps. **⚠️:** wake-word models run on-device for privacy/latency.

#### Speech translation
- **What & why:** translate spoken input — **speech-to-text** or **speech-to-speech** — across languages, live. **✅ Use when:**
  multilingual meetings/support. **🚫 Avoid → Translator:** for text-only. **⚠️:** latency matters for live use.

> 🔬 **Under the hood:** one **Azure AI Speech** resource + SDK. SSML is XML wrapping your text; **custom speech**
> fine-tunes the recogniser on your audio; speech translation chains STT → translation (→ TTS for speech-out).

### 💻 The SDK in code
```python
# pip install azure-cognitiveservices-speech
import azure.cognitiveservices.speech as speechsdk

speech_config = speechsdk.SpeechConfig(subscription="<key>", region="<region>")

# --- Speech-to-text (one utterance) ---
speech_config.speech_recognition_language = "en-US"
audio_in = speechsdk.audio.AudioConfig(use_default_microphone=True)  # or filename="call.wav"
recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_in)
stt = recognizer.recognize_once_async().get()
if stt.reason == speechsdk.ResultReason.RecognizedSpeech:
    print(stt.text)

# --- Text-to-speech (neural voice; use speak_ssml_async for fine control) ---
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
synth = speechsdk.SpeechSynthesizer(speech_config=speech_config)
synth.speak_text_async("Your balance is 42 pounds.").get()
```
SSML directs *how* it speaks:
```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
  <voice name="en-US-JennyNeural">
    <prosody rate="-10%" pitch="+5%">Hello <break time="300ms"/> there.</prosody>
    <say-as interpret-as="telephone">5550123</say-as>
  </voice>
</speak>
```

### 📦 SDK & API quick reference
| Thing | Value |
|---|---|
| pip package | `azure-cognitiveservices-speech` |
| Config | `SpeechConfig(subscription, region)` · `AudioConfig(use_default_microphone / filename)` |
| STT | `SpeechRecognizer.recognize_once_async()` (single) · `start_continuous_recognition()` (stream) |
| TTS | `SpeechSynthesizer.speak_text_async()` / `speak_ssml_async()` |
| Voices | neural, e.g. `en-US-JennyNeural`, `en-US-GuyNeural` |
| SSML tags | `<speak> <voice> <prosody rate/pitch/volume> <break> <say-as> <phoneme> <lexicon> <mstts:express-as>` |
| Translation | `SpeechTranslationConfig` + `TranslationRecognizer.add_target_language(...)` |
| Keyword | `KeywordRecognizer` + keyword model; intent via CLU |

### 🎯 Exam facts to memorise
- One package: **`azure-cognitiveservices-speech`**; everything hangs off **`SpeechConfig(subscription, region)`**.
- **STT:** `recognize_once_async()` = a single utterance; **continuous** recognition for long audio/streams.
- **TTS:** neural voices (`en-US-JennyNeural`…); use **`speak_ssml_async`** when you need SSML control.
- **SSML** controls pronunciation/delivery: `<prosody>` (rate/pitch/volume), `<break>`, `<say-as>`, `<phoneme>`, `<lexicon>`, `<mstts:express-as>` (speaking style).
- **Custom Speech** = customise **STT** (your audio/jargon); **Custom Neural Voice** = customise **TTS** (a brand voice).
- **Speech translation** uses `SpeechTranslationConfig` + `TranslationRecognizer` (speech-to-text or speech-to-speech).

## 🚀 Stage 3 — In Practice / Why It Matters
A call centre transcribes calls (**STT**), reads back answers (**TTS** + **SSML** for natural delivery), trains
**custom speech** on product names, takes voice commands (**keyword/intent**), and offers live **speech translation**
for foreign-language callers. On the exam: "transcribe" → STT; "speak/voice" → TTS; "pronunciation/prosody" → SSML;
"our jargon misheard" → custom speech; "live cross-language voice" → speech translation.

## ⚖️ Variations & When to Use
| The need is… | Use |
|---|---|
| Transcribe audio | **STT** |
| Speak text aloud | **TTS** |
| Fix pronunciation / delivery | **SSML** |
| Recognise your jargon/accent | **Custom speech** |
| Wake-word / voice command | **Keyword / intent** |
| Live cross-language voice | **Speech translation** |
| Translate *text* only | **Translator** (Lesson 01) |

## 🐛 Common Errors & Fixes
| Symptom | Cause | Fix |
|---|---|---|
| Brand name mispronounced | default delivery | **SSML** (lexicon/phoneme); custom voice if persistent |
| Jargon mis-transcribed | generic STT | train **custom speech** |
| Flat, robotic voice | no prosody control | **SSML** (pitch/rate/pauses) |
| Used Translator for spoken audio | text-only tool | use **speech translation** |

## 📌 Quick Reference
- **Listen → STT · Speak → TTS · Direct delivery → SSML · Your jargon → custom speech · Wake-word/command →
  keyword/intent · Live cross-language voice → speech translation.**
- Try **SSML markup before** training a custom voice.

## 🎯 Exam-style practice
**Q1.** A brand name is mispronounced by the neural voice. Cheapest fix, and which method applies it?
<details><summary>Answer</summary>Use **SSML** (`<phoneme>`/`<lexicon>`, or `<prosody>` for delivery) and synthesise with **`speak_ssml_async(...)`** — no custom voice training needed.</details>

**Q2.** You must transcribe a **long, continuous** call, not a single sentence. Which API?
<details><summary>Answer</summary>**Continuous recognition** — `start_continuous_recognition()` with event handlers, not `recognize_once_async()` (one utterance only).</details>

**Q3.** A Spanish caller must reach an English agent **live by voice**. Which config + recognizer?
<details><summary>Answer</summary>**`SpeechTranslationConfig`** with `add_target_language("en")` and a **`TranslationRecognizer`** (speech translation) — not the text Translator.</details>

## 🛑 STOP — Self-Check
A bank's voice bot (a) keeps **mispronouncing its product names and sounds robotic**, and (b) must let a
**Spanish-speaking caller talk to an English agent live**. Which Speech features fix each — and which to try first for (a)?

<details><summary>Answer</summary>

- **(a) Pronunciation + robotic delivery → SSML first** (set pronunciation, pitch, pace, pauses) — it's the
  cheap fix; only train a **custom voice / custom speech** if the jargon problem persists.
- **(b) Live Spanish↔English voice → speech translation** (speech-to-text or speech-to-speech), not the text
  Translator.

Rule of thumb: markup (SSML) before retraining; speech translation for spoken cross-language, Translator for text.
</details>

⏭️ **Next:** 03 — Custom Language (CLU) & Question Answering (Branch 5.3).
