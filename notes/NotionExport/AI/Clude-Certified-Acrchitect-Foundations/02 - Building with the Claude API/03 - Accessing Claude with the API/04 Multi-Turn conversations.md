# 04 — Multi-Turn Conversations

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 4 of 10 · [← Prev: Making a Request](03%20Making%20a%20request.md) · [Course Index](../README.md) · [Next: Chat Exercise →](05%20Chat%20exercise.md)

---

## 🗺️ Concept Overview

When working with the Anthropic API and Claude, there is a fundamental architectural concept you must understand: **Claude does not store any of your conversation history**. Each request you make is completely independent and stateless, with zero memory of previous exchanges.

![Claude Does Not Store Conversation History](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_004_-_Multi-Turn_Conversations_01.1748623269971.png)

This means if you want to have a multi-turn conversation where Claude remembers context from earlier messages, **you must manage and track the conversation state yourself** in your application code.

---

## ⚠️ The Problem with Stateless Conversations

Consider what happens if you ask Claude: *"What is quantum computing?"* and receive a clear explanation. 

If you immediately follow up with a second request: *"Write another sentence"*, Claude will have no idea what you are referring to. Because each call is stateless, Claude sees only the isolated prompt *"Write another sentence"* and will generate a random sentence about an unrelated topic:

![Stateless Follow-up Failure](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623270%2F03_-_004_-_Multi-Turn_Conversations_02.1748623270625.png)

Without conversation history, the model lacks the context needed to understand anaphora, references, and follow-up requests.

---

## 🔄 How Multi-Turn Conversations Work

To maintain conversation context across exchanges, your application must handle two responsibilities:

1. **Manually maintain a list of all messages** in your application state.
2. **Send the complete message history** with every subsequent request.

![Multi-Turn Solution: Maintain History and Send Full List](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623271%2F03_-_004_-_Multi-Turn_Conversations_05.1748623271251.png)

### The 4-Step Multi-Turn Flow

![The 4-Step Multi-Turn Flow](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623271%2F03_-_004_-_Multi-Turn_Conversations_08.1748623271832.png)

```text
Turn 1:
1. Send initial user message:
   messages = [{"role": "user", "content": "Define quantum computing in one sentence"}]

2. Receive response and append as assistant message:
   messages = [
     {"role": "user", "content": "Define quantum computing in one sentence"},
     {"role": "assistant", "content": "Quantum computing harnesses superposition and entanglement..."}
   ]

Turn 2:
3. Append user follow-up question:
   messages = [
     {"role": "user", "content": "Define quantum computing in one sentence"},
     {"role": "assistant", "content": "Quantum computing harnesses superposition and entanglement..."},
     {"role": "user", "content": "Write another sentence"}
   ]

4. Send the ENTIRE message history to Claude:
   Claude reads turns 1 and 2, recognizes the context, and provides a relevant follow-up!
```

---

## 🛠️ Building Helper Functions

To make conversation management clean and reusable across your code, create three standard helper functions:

```python
def add_user_message(messages: list, text: str) -> None:
    """Appends a user turn to the conversation history."""
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages: list, text: str) -> None:
    """Appends an assistant turn to the conversation history."""
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

def chat(messages: list) -> str:
    """Dispatches the complete message history to Claude and returns the generated text."""
    message = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=messages,
    )
    return message.content[0].text
```

---

## 🚀 Putting It All Together

Here is how you use these helper functions to conduct a multi-turn conversation with full context retention:

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
model = "claude-3-7-sonnet-20250219"

# 1. Start with an empty message list
messages = []

# 2. Add initial user question
add_user_message(messages, "Define quantum computing in one sentence")

# 3. Get Claude's response
answer = chat(messages)
print(f"Claude: {answer}\n")

# 4. Add Claude's response to the conversation history
add_assistant_message(messages, answer)

# 5. Add follow-up question
add_user_message(messages, "Write another sentence")

# 6. Get the follow-up response with full context
final_answer = chat(messages)
print(f"Claude (Follow-up): {final_answer}")
```

Now Claude understands that *"Write another sentence"* refers directly to expanding upon quantum computing, because the model received the entire conversational trajectory.

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                    MULTI-TURN STATE RULES SUMMARY                      │
├───────────────────────┬────────────────────────────────────────────────┤
│ API Memory Storage    │ NONE (The API is completely stateless)         │
│ State Location        │ Client / Application Server memory             │
│ History Format        │ List of dicts: `{"role": ..., "content": ...}` │
│ Turn Sequence         │ Alternating: `user` ──► `assistant` ──► `user` │
│ Token Impact          │ Input token usage grows with each turn         │
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
Why does Claude fail to understand a follow-up query like *"Can you give me an example of that?"* if you send only that query in `messages`?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Because the Anthropic API is completely stateless and stores no memory between requests. If you only send the latest query, Claude has no record of the previous turns and does not know what "that" refers to.
</details>

---

### Question 2
What role do you assign to Claude's responses when appending them back into the `messages` array for a subsequent turn?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** `"role": "assistant"`.

**Explanation:** In the Messages API, human inputs are labeled with `"role": "user"`, while model completions are recorded with `"role": "assistant"`. The API requires message roles to alternate properly to maintain conversation structure.
</details>
