# 03 — Making a Request

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 3 of 10 · [← Prev: Getting an API Key](02%20Getting%20an%20API%20key.md) · [Course Index](../README.md) · [Next: Multi-Turn Conversations →](04%20Multi-Turn%20conversations.md)

---

## 🗺️ Concept Overview

Making your first request to the Anthropic API is straightforward once you understand the basic setup and structure. This guide walks through the essential steps to get Claude responding to your prompts using Python.

---

## 🛠️ Setting Up Your Environment

Before making any API calls, you need to install the required packages and configure your API key securely.

### 1. Install Dependencies
In your terminal or Jupyter notebook, install the official Anthropic SDK and `python-dotenv`:

```bash
%pip install anthropic python-dotenv
```

### 2. Store Your API Key in `.env`
Create a `.env` file in the same directory as your script or notebook to store your API key securely:

```env
ANTHROPIC_API_KEY="your-api-key-here"
```

> [!IMPORTANT]
> This approach keeps your API key out of your code and prevents accidentally committing it to version control. Always add `.env` to your `.gitignore` file.

### 3. Initialize the Client
Load the environment variable and create your Anthropic client:

```python
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic()
model = "claude-3-7-sonnet-20250219"  # Or claude-3-5-haiku-20241022
```

---

## ⚙️ The Create Function

The core method for dispatching API requests is **`client.messages.create()`**. 

This function requires three key parameters:

![The Create Function Parameters](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623269%2F03_-_003_-_Making_a_Request_09.1748623269461.png)

| Parameter | Type | Description |
| :--- | :--- | :--- |
| **`model`** | `str` | The name of the Claude model you want to use. |
| **`max_tokens`** | `int` | A safety limit on response length (not a target length). |
| **`messages`** | `list[dict]` | The conversation history sent to Claude. |

### Understanding `max_tokens` as a Safety Mechanism
The `max_tokens` parameter acts as a **safety ceiling**, not a target generation length:
- If you set `max_tokens=1000`, Claude will stop generating after 1000 tokens even if it has more to say.
- Claude does not try to reach this limit; it writes what it deems appropriate and terminates naturally (`end_turn`) unless it hits the maximum ceiling first.

---

## 💬 Understanding Messages

Messages represent the ongoing conversation between you and Claude, similar to a chat application.

![Understanding User and Assistant Messages](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_003_-_Making_a_Request_13.1748623270369.png)

There are two primary message types:
- **User messages (`"role": "user"`):** Content sent to Claude, authored by humans or client applications.
- **Assistant messages (`"role": "assistant"`):** Responses that Claude has generated.

Each message is represented as a dictionary with two fields:
1. `role`: Either `"user"` or `"assistant"`.
2. `content`: The text string payload.

---

## 🚀 Making Your First Request

Here is a complete, standalone example of making a request to Claude:

```python
from dotenv import load_dotenv
from anthropic import Anthropic

# 1. Load API key from .env
load_dotenv()

# 2. Instantiate client
client = Anthropic()
model = "claude-3-7-sonnet-20250219"

# 3. Create message request
message = client.messages.create(
    model=model,
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence"
        }
    ]
)
```

When you run this code, Claude processes your request and returns a structured `Message` response object containing the generated text along with metadata.

---

## 📄 Extracting the Response

The response object contains metadata and usage statistics, but you typically want just the generated text content. Access it via:

```python
generated_text = message.content[0].text
print(generated_text)
```

### Example Output:
> *"Quantum computing is a type of computation that leverages quantum mechanics principles like superposition and entanglement to process information using quantum bits (qubits), potentially solving certain complex problems exponentially faster than classical computers."*

### Inspecting Response Metadata:
```python
print(f"Stop Reason   : {message.stop_reason}")
print(f"Input Tokens  : {message.usage.input_tokens}")
print(f"Output Tokens : {message.usage.output_tokens}")
```

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                      MESSAGES API QUICK TEMPLATE                       │
├────────────────────────────────────────────────────────────────────────┤
│ from dotenv import load_dotenv                                         │
│ from anthropic import Anthropic                                        │
│                                                                        │
│ load_dotenv()                                                          │
│ client = Anthropic()                                                   │
│                                                                        │
│ res = client.messages.create(                                          │
│     model="claude-3-7-sonnet-20250219",                                │
│     max_tokens=1000,                                                   │
│     messages=[{"role": "user", "content": "Your prompt here"}]         │
│ )                                                                      │
│                                                                        │
│ text = res.content[0].text                                             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
If you set `max_tokens=500` in a request and ask Claude a simple greeting like *"Hello, how are you?"*, will Claude generate 500 tokens?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** No. Claude will generate a brief, natural response (typically 10–25 tokens) and stop with `stop_reason="end_turn"`.

**Explanation:** `max_tokens` is a safety ceiling, not a target word count. Claude does not pad its response to reach `max_tokens`.
</details>

---

### Question 2
How do you extract the plain generated text string from the response object returned by `client.messages.create()`?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** By accessing `message.content[0].text`.

**Explanation:** The response object's `content` attribute is a list of content blocks. For standard text completions, the first block (`content[0]`) is a `TextBlock` whose `.text` property holds the generated string.
</details>
