# 08 — Temperature

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 8 of 10 · [← Prev: System Prompts Exercise](07%20System%20prompts%20exercise.md) · [Course Index](../README.md) · [Next: Response Streaming →](09%20Response%20streaming.md)

---

## 🗺️ Concept Overview

Temperature is a powerful parameter that controls how predictable or creative Claude's responses will be. Understanding how to calibrate temperature effectively allows you to fine-tune Claude for both deterministic data extraction and open-ended creative brainstorming.

---

## ⚙️ How Claude Generates Text

To understand temperature, it helps to understand how Claude constructs text step-by-step. When you send Claude a prompt like *"What do you think?"*, the model processes it in three stages:

1. **Tokenization:** Breaking your input text into smaller pieces (tokens).
2. **Prediction:** Calculating probability scores for all potential next tokens in its vocabulary.
3. **Sampling:** Selecting a token based on those probability distributions.

![How Claude Generates Text: Tokenization, Prediction, Sampling](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623338%2F03_-_008_-_Temperature_00.1748623338635.png)

In this example, after processing *"What do you think"*, Claude might calculate:
- `"about"`: **30%**
- `"would"`: **20%**
- `"of"`: **10%**
- Other candidate tokens: remaining percentage

Claude samples one token, appends it to the sequence, and repeats the entire cycle autoregressively to construct full sentences:

![Autoregressive Token Sampling Loop](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623339%2F03_-_008_-_Temperature_05.1748623339740.png)

---

## 🎛️ What Temperature Does

Temperature is a decimal value between **0.0 and 1.0** that directly scales these token selection probabilities. It acts as an adjustable **creativity dial**:

![Temperature Dial: 0.0 to 1.0](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623340%2F03_-_008_-_Temperature_06.1748623340446.png)

- **Low Temperature (near 0.0):** Claude becomes highly deterministic, almost always selecting the single highest-probability token.
- **High Temperature (near 1.0):** Claude flattens the probability distribution, giving lower-ranked tokens a higher chance of selection, leading to more varied and creative responses.

---

## 📊 Probability Distribution Comparison

![Interactive Temperature Demo: 0.0 vs 1.0](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623341%2F03_-_008_-_Temperature_07.1748623341049.png)

- **At Temperature 0.0:** The top candidate (`"about"`) receives **100%** of the selection probability—rendering the generation fully deterministic.
- **At Temperature 1.0:** Probabilities spread more evenly across candidate tokens (`"about"`, `"would"`, `"of"`), introducing controlled randomness and diverse phrasing.

---

## 🎯 Choosing the Right Temperature

Different operational tasks require different temperature bands:

![Choosing the Right Temperature Range](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623341%2F03_-_008_-_Temperature_10.1748623341732.png)

| Temperature Range | Behavior Profile | Best Used For |
| :--- | :--- | :--- |
| **Low (0.0 – 0.3)** | Predictable, focused, deterministic | • Factual question answering<br>• Coding assistance and syntax generation<br>• Data extraction and JSON parsing<br>• Content moderation and classification |
| **Medium (0.4 – 0.7)** | Balanced fluency with moderate variation | • Document summarization<br>• Educational explanations<br>• General problem solving<br>• Creative writing with strict constraints |
| **High (0.8 – 1.0)** | Diverse, surprising, creative | • Open brainstorming<br>• Creative storytelling and poetry<br>• Marketing copy and ad angles<br>• Joke generation and humor |

---

## 💻 Implementing Temperature in Code

You can add temperature support to your existing `chat` helper function by passing it into the parameters dictionary:

```python
def chat(messages: list, system: str | None = None, temperature: float = 1.0) -> str:
    params = {
        "model": model,
        "max_tokens": 1000,
        "messages": messages,
        "temperature": temperature  # Injects temperature parameter
    }
    
    if system:
        params["system"] = system
    
    message = client.messages.create(**params)
    return message.content[0].text
```

### Testing Temperature Effects in Action:

```python
prompt = "Pitch an original movie idea in one sentence."
messages = [{"role": "user", "content": prompt}]

# 1. Low Temperature (0.0) - Highly predictable across runs:
answer_low = chat(messages, temperature=0.0)
print("Low Temp (0.0):", answer_low)
# Typical output: "A time-traveling archaeologist must prevent ancient artifacts from being stolen."

# 2. High Temperature (1.0) - High variation and novel angles:
answer_high = chat(messages, temperature=1.0)
print("High Temp (1.0):", answer_high)
# Typical output: "In a world where memories can be physically traded like currency, an undercover sensory-thief uncovers an illegal black market of fabricated childhoods."
```

---

## 💡 Key Takeaways

1. **Temperature alters probabilities, not guarantees:** High temperature does not guarantee completely different output every time; it simply expands the likelihood of sampling alternative tokens.
2. **Match temperature to your task:**
   - Need exact, reproducible facts or JSON schema adherence? **Use 0.0.**
   - Need creative brainstorming? **Dial up to 0.8–1.0.**
   - Need general assistance and conversation? **0.5–0.7 works well.**

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        TEMPERATURE QUICK REFERENCE                     │
├───────────────────────┬────────────────────────────────────────────────┤
│ Parameter Range       │ `0.0` to `1.0` (float)                         │
│ Default Value         │ `1.0`                                          │
│ At 0.0                │ Greedy decoding; selects top token every time  │
│ At 1.0                │ Maximum token probability flattening           │
│ Recommended for Code  │ `0.0` (strict deterministic syntax)            │
│ Recommended for Brain │ `0.8 - 1.0` (diverse conceptual variation)     │
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
Why should an API call designed to extract structured JSON data from invoice documents use `temperature=0.0` rather than `temperature=1.0`?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** At `temperature=0.0`, Claude operates deterministically and consistently selects the highest-probability tokens. This minimizes hallucinations, prevents invalid schema deviations, and ensures syntax consistency (such as matching brackets and quotes) required for reliable JSON parsing.
</details>

---

### Question 2
Does setting `temperature=1.0` guarantee that Claude will never repeat a response?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** No. Temperature adjusts the probability distribution across tokens, increasing the chance of variation, but does not guarantee unique outputs. If a prompt strongly constrains the vocabulary (e.g. *"What is $2 + 2$?"*), the top token probability remains so overwhelmingly high that Claude will still select it.
</details>
