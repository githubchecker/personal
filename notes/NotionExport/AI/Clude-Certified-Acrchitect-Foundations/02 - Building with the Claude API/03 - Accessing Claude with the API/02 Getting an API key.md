# 02 — Getting an API Key

> Course 02 · Section 03 - Accessing Claude with the API · Lesson 2 of 10 · [← Prev: Accessing the API](01%20Accessing%20the%20API.md) · [Course Index](../README.md) · [Next: Making a Request →](03%20Making%20a%20request.md)

---

## 🗺️ Concept Overview

To make programmatic calls to Claude via the Anthropic API, your backend application requires a **secret API key** for authentication and billing attribution. 

This guide details the step-by-step process of provisioning an API key in the Anthropic Console, naming and scoping it appropriately, and securing it against accidental exposure.

---

## 🔑 Step-by-Step API Key Provisioning

### Step One: Navigate to the Anthropic API Console
Open your web browser, navigate to [https://console.anthropic.com/](https://console.anthropic.com/), and sign in to your Anthropic account.

Upon logging in, you will be greeted by the primary console dashboard:

![Step 1: Anthropic Console Dashboard](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846091%2FScreenshot+2025-06-13+at+2.20.45%E2%80%AFPM.1749846091092.png)

---

### Step Two: Click the 'Get API Keys' Button
Locate and click the **'Get API Keys'** button positioned near the top right of the dashboard view:

![Step 2: Get API Keys Button](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846107%2FScreenshot+2025-06-13+at+2.21.16%E2%80%AFPM.1749846106943.png)

---

### Step Three: Click the 'Create Key' Button
On the API Keys management page, click the **'Create Key'** button located in the upper right section:

![Step 3: Create Key Button](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846149%2FScreenshot+2025-06-13+at+2.22.10%E2%80%AFPM.1749846149203.png)

---

### Step Four: Select Workspace and Name Your Key
In the modal dialog that appears:
1. **Workspace:** Select your target workspace (default is `'Default'`).
2. **Key Name:** Enter a descriptive identifier to help you track its usage (for example, `'Anthropic Course'`).

![Step 4: Select Workspace and Key Name](https://everpath-course-content.s3-accelerate.amazonaws.com/instructor%2Fa46l9irobhg0f5webscixp0bs%2Fpublic%2F1749846167%2FScreenshot+2025-06-13+at+2.22.14%E2%80%AFPM.1749846166954.png)

---

### Step Five: Copy and Secure the Key
Your new API key (prefixed with `sk-ant-api03-...`) will appear inside a confirmation pop-up window:

> [!CAUTION]
> **This key will only be displayed once!** Make sure to copy it immediately and store it securely.
> If you close the window without copying the key, you cannot retrieve it later. You must delete the key and generate a new one.

---

## 🛡️ Best Practices for Key Security

1. **Never Commit Secrets to Version Control:**
   - Store your key locally in a `.env` file:
     ```env
     ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
     ```
   - Ensure `.env` is listed inside `.gitignore` before making any git commits:
     ```gitignore
     .env
     ```
2. **Use Descriptive Labels:**
   - Name keys by environment or microservice (e.g. `dev-document-parser`, `prod-customer-service`) so that team members can trace billing and revoke individual keys cleanly.
3. **Revocation on Compromise:**
   - If an API key is accidentally exposed in public code or logs, immediately navigate back to the Console, locate the key row, and click **Delete / Revoke**.

---

## 📌 Quick Reference

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        API KEY PROVISIONING CHEATSHEET                 │
├───────────────────────┬────────────────────────────────────────────────┤
│ Console URL           │ https://console.anthropic.com/                 │
│ Key Prefix Format     │ `sk-ant-api03-...`                             │
│ Workspace Scope       │ Default (or team-specific workspace)           │
│ Visibility Policy     │ Displayed ONCE upon generation                 │
│ Local Storage         │ `.env` file (strictly excluded via `.gitignore`)│
└───────────────────────┴────────────────────────────────────────────────┘
```

---

## 🛑 Self-Check

### Question 1
What must you do if you generate an API key in the Anthropic Console, close the pop-up modal, and realize you forgot to copy the key string?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** You must delete the lost key and generate a brand-new API key.

**Explanation:** For security reasons, the Anthropic Console only displays the plaintext secret string once at generation time. It is never stored in recoverable plaintext on Anthropic's console interface after the dialog is closed.
</details>

---

### Question 2
Why should developers assign descriptive names (like `Anthropic Course` or `dev-search-service`) rather than generic names when creating API keys?

<details>
<summary>👉 Reveal Answer & Explanation</summary>

**Answer:** Descriptive names allow you to identify which application, team, or environment is consuming tokens, track spend attribution, and safely revoke a compromised or decommissioned key without breaking other active services.
</details>
