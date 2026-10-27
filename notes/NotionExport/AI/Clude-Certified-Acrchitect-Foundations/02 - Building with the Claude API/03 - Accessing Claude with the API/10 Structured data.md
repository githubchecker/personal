# 10 — Structured Data

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 10 of 10 · [← Prev: Response Streaming](09%20Response%20streaming.md) · [Course Index](../README.md) · [Next: Prompt Evaluation →](../04%20-%20Prompt%20evaluation/01%20Prompt%20evaluation.md)

---

## 🗺️ Concept Overview

When you need Claude to generate structured data—such as JSON, Python code, or bulleted lists—you will often encounter a common challenge: Claude naturally wants to be helpful and adds explanatory text around your content. 

While conversational commentary is helpful in human chat, software applications often require **pure, raw data** that can be directly parsed, copied, or ingested by downstream systems without manual cleanup.

![Structured Data Problem: Web App Generating EventBridge Rules](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623326%2F03_-_011_-_Structured_Data_02.1748623325858.png)

### The Production Scenario
Consider building a web application that generates AWS EventBridge rules. Users type a description, click "Generate", and expect to see clean JSON they can immediately copy and paste into their cloud infrastructure. 

If Claude returns the JSON wrapped in markdown formatting with conversational footers, users cannot simply click "Copy All"—they must manually select only the JSON portion, creating friction.

---

## ⚠️ The Problem with Default Responses

By default, asking Claude to generate JSON produces an answer like this:

````markdown
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
```

This rule captures EC2 instance state changes when instances start running.
````

The JSON syntax itself is correct, but because it is wrapped inside markdown code fences and followed by explanatory commentary, programmatic ingestion via `json.loads()` will fail with a decode error.

---

## 💡 The Solution: Assistant Prefilling + Stop Sequences

You can combine **assistant message prefilling** with **stop sequences** to instruct Claude to output strictly the raw content you want:

```python
messages = []

# 1. User message specifies the target task
add_user_message(messages, "Generate a very short event bridge rule as json")

# 2. Prefill an assistant message with the opening code block
add_assistant_message(messages, "```json")

# 3. Halt generation the instant Claude attempts to close the block
text = chat(messages, stop_sequences=["```"])
```

![Assistant Message Prefilling and Stop Sequences Mechanism](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623327%2F03_-_011_-_Structured_Data_15.1748623326804.png)

### How This Mechanism Operates:
1. **Task Definition:** The user message instructs Claude what to generate.
2. **Context Assumption:** The prefilled assistant message makes Claude assume it has *already* started its response with ```` ```json ````. Because autoregressive models only generate forward from the end of the context, Claude immediately writes the JSON body without generating an introductory greeting.
3. **Pure Content Generation:** Claude outputs only the interior JSON payload.
4. **Immediate Halting:** As soon as Claude finishes the JSON and emits the closing fence (```` ``` ````), the stop sequence triggers, immediately halting generation and omitting the closing sequence from the returned text.

### The Resulting Clean Output:
```json
{
  "source": ["aws.ec2"],
  "detail-type": ["EC2 Instance State-change Notification"],
  "detail": {
    "state": ["running"]
  }
}
```

---

## 🛠️ Processing the Response

Because the model begins generating on the line immediately following the prefill, the raw returned string may have leading or trailing whitespace. Clean it using Python's `.strip()` before parsing:

```python
import json

# Clean up whitespace and parse cleanly with zero regex
clean_json = json.loads(text.strip())

print(clean_json["source"])  # Output: ['aws.ec2']
```

---

## 🌐 Beyond JSON

This technique is not limited to JSON. You can apply it whenever you need raw, clean content without conversational commentary:

- **Python Code Snippets:** Prefill with ```` ```python ```` and stop at ```` ``` ````.
- **CSV Data:** Prefill with header rows and stop at a custom sequence.
- **Bulleted Lists:** Prefill with the first bullet symbol (e.g. `"- "`).
- **SQL Queries:** Prefill with ```` ```sql ```` and stop at ```` ``` ```` (or `;`).

> [!TIP]
> **The General Rule:** Identify what container Claude naturally wants to wrap your content in (such as a markdown code fence), and use the opening marker as your **prefill** and the closing marker as your **stop sequence**.

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   STRUCTURED DATA EXTRACTION PATTERN                   │
├───────────────────────┬────────────────────────────────────────────────┤
│ Goal                  │ Zero preamble, zero postscript, 100% clean data│
│ Step 1: User Message  │ "Generate <target> as JSON"                    │
│ Step 2: Prefill       │ `add_assistant_message(messages, "```json")`   │
│ Step 3: Stop Sequence │ `chat(messages, stop_sequences=["```"])`       │
│ Step 4: Parse         │ `data = json.loads(text.strip())`              │
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
Why does Claude omit conversational greetings like *"Sure, here is the JSON you requested:"* when an assistant message containing ```` ```json ```` is prefilled?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because Claude sees the prefilled assistant message as text it has already written. Since generation proceeds strictly forward from the end of the context, Claude cannot backtrack to insert introductory phrases before its own prior output.
</details>

---

### Question 2
When using `stop_sequences=["```"]`, does the returned string in `text` include the closing ```` ``` ````?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** No. When generation halts due to a matched stop sequence, the matched delimiter itself is omitted from the final returned response text.
</details>
