# 01 — Accessing the API

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 1 of 10 · [Course Index](../README.md) · [Next: Getting an API Key →](02%20Getting%20an%20API%20key.md)

---

## 🗺️ Concept Overview

When building applications with Claude, understanding the complete request lifecycle helps you make better architectural decisions and debug issues more effectively. Let's walk through what happens from the moment a user clicks "send" in your chat interface to when Claude's response appears on screen.

![Accessing the API Overview](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623274%2F03_-_001_-_Accessing_the_API_01.1748623274598.png)

---

## 🔄 The Five-Step Request Flow

Every interaction with Claude follows a predictable pattern with five distinct phases: **request to server**, **request to Anthropic API**, **model processing**, **response to server**, and **response to client**.

![The Five-Step Request Flow](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623275%2F03_-_001_-_Accessing_the_API_03.1748623275310.png)

```text
[ 1. End User Client ] (Web / Mobile App)
          │
          │ 1. User sends prompt via HTTPS
          ▼
[ 2. Your Application Server ] ──── (Securely holds Secret API Key)
          │
          │ 2. Dispatches request via SDK / HTTP (Model, Messages, Max Tokens)
          ▼
[ 3. Anthropic API / Claude ]
          │
          │ 3. Model Processing:
          │    [ Tokenization ] ──► [ Embedding ] ──► [ Contextualization ] ──► [ Generation ]
          │
          │ 4. Returns structured payload (Message, Usage, Stop Reason)
          ▼
[ 4. Your Application Server ]
          │
          │ 5. Forwards clean response text to client
          ▼
[ 5. End User Client ] (Displays response in UI)
```

---

## 🛡️ Why You Need a Server

You should **never** make requests to the Anthropic API directly from client-side code. Here's why:

- **API requests require a secret API key for authentication.**
- **Exposing this key in client code creates a serious security vulnerability:** Any user or attacker can inspect client-side JavaScript or decompile mobile binaries to extract your key.
- **Unauthorized requests:** Anyone who extracts the key can make unauthorized requests and run up massive bills on your account.

Instead, your web or mobile app sends requests to **your own backend server**, which then communicates with the Anthropic API using the securely stored key.

---

## 📤 Making API Requests

When your server contacts the Anthropic API, you can use either an official SDK or make plain HTTP requests. Anthropic provides SDKs for **Python, TypeScript, JavaScript, Go, and Ruby**.

![Making API Requests](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623276%2F03_-_001_-_Accessing_the_API_05.1748623276722.png)

### Essential Request Fields
Every request must include these essential fields:

| Field | Description | Example |
| :--- | :--- | :--- |
| **API Key** | Identifies your request to Anthropic and authorizes billing. | Passed via `x-api-key` header or SDK client initialization |
| **Model** | Name of the model to use. | `"claude-3-7-sonnet-20250219"`, `"claude-3-5-haiku-20241022"` |
| **Messages** | List containing the user's input text turns. | `[{"role": "user", "content": "What is quantum computing?"}]` |
| **Max Tokens** | Safety limit for how many tokens Claude can generate. | `max_tokens=1000` |

---

## ⚙️ Inside Claude's Processing

Once Anthropic receives your request, Claude processes it through four main stages: **tokenization**, **embedding**, **contextualization**, and **generation**.

![Inside Claude's Processing](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623277%2F03_-_001_-_Accessing_the_API_08.1748623277503.png)

### 1. Tokenization
Claude first breaks your input text into smaller chunks called **tokens**. These can be whole words, parts of words, spaces, or symbols. 
- For simplicity, think of each word as one token.

### 2. Embedding
Each token gets converted into an **embedding**—a long list of numbers that represents all possible meanings of that word. Think of embeddings as numerical definitions that capture semantic relationships.

![Embedding: Numerical Definitions of Word Meanings](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623278%2F03_-_001_-_Accessing_the_API_10.1748623278148.png)

Words often have multiple meanings. For example, `"quantum"` could refer to:
- A discrete unit of physical quantity (physics)
- Quantum mechanics or quantum physics concepts
- Something extremely small or subatomic
- Quantum computing applications

### 3. Contextualization
Claude refines each embedding based on surrounding words to determine the most likely meaning in context. This process adjusts the numerical representations to highlight the appropriate definition.

![Contextualization: Refining Embeddings Based on Surrounding Words](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623278%2F03_-_001_-_Accessing_the_API_11.1748623278717.png)

### 4. Generation
The contextualized embeddings pass through an output layer that calculates probabilities for each possible next word. Claude doesn't always pick the highest probability word—it uses a mix of probability and controlled randomness to create natural, varied responses.

![Generation: Output Probabilities and Token Selection](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623279%2F03_-_001_-_Accessing_the_API_13.1748623279317.png)

After selecting each word, Claude adds it to the sequence and repeats the entire process autoregressively for the next word.

---

## 🛑 When Claude Stops Generating

After each token, Claude checks several conditions to decide whether to continue:

![When Claude Stops Generating](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623280%2F03_-_001_-_Accessing_the_API_15.1748623279963.png)

- **Max tokens reached:** Has it hit the limit you specified in `max_tokens`?
- **Natural ending:** Did it generate an end-of-sequence token (`<end_of_sequence>`)?
- **Stop sequence:** Did it encounter a predefined stop phrase specified in `stop_sequences`?

---

## 📥 The API Response

When generation completes, the API sends back a structured response containing:

- **Message (`content`):** The generated text.
- **Usage (`usage`):** Count of input and output tokens.
- **Stop Reason (`stop_reason`):** Why generation ended (`end_turn`, `max_tokens`, `stop_sequence`).

![The API Response Structure](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623281%2F03_-_001_-_Accessing_the_API_17.1748623281653.png)

Your server receives this response and forwards the generated text back to your client application, where it appears in the user interface.

![Forwarding the Response Back to Client](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1748623282%2F03_-_001_-_Accessing_the_API_19.1748623282180.png)

---

## 💡 Key Takeaways

Understanding this request lifecycle helps you:
1. **Design secure architectures** that protect your secret API keys behind server-side proxies.
2. **Set appropriate token limits (`max_tokens`)** to balance response completeness and cost.
3. **Handle different stop reasons** (`end_turn` vs. `max_tokens` vs. `stop_sequence`) in your application logic.
4. **Debug issues effectively** by knowing where they might occur in the pipeline (client $\leftrightarrow$ server $\leftrightarrow$ Anthropic API).

---

## 🛑 Self-Check

### Question 1
Why must API requests to Anthropic be made through your own backend server rather than directly from a client application?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** To protect your secret API key. Client-side applications (such as browsers or mobile apps) execute on user devices where code can be inspected. If the API key is included in client code, unauthorized parties can extract it and make unauthorized API calls billed to your account.
</details>

---

### Question 2
What role does **Contextualization** play after Claude converts tokens into embeddings?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Words often have multiple possible meanings (e.g., "quantum" in physics vs. quantum computing). The embedding captures all possible meanings, while contextualization uses the surrounding words to refine the embedding so it represents the exact intended meaning in that specific context.
</details>
