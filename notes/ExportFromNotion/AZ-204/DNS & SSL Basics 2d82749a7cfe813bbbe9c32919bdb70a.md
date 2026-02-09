# DNS & SSL Basics

# **The Analogy: A Secure Conversation in a Crowded Post Office**

- Imagine you need to send a secret message to your bank manager, Alice, who works at the "Bank of Contoso".
    - **1. Finding the Bank (DNS: A and CNAME Records)**
        - You know the bank's name ("Bank of Contoso"), but not its street address. This name is your **domain name**.
        - You look up "Bank of Contoso" in a global address book. This is **DNS**.
        - The address book might say: "For 'Bank of Contoso' ([www.contoso.com](http://www.contoso.com/)), see the address for 'Azure Central Processing Center' ([contoso.azurewebsites.net](http://contoso.azurewebsites.net/))." This is a **CNAME Record**. It's an alias. It points a name to another name.
        - Then you look up "Azure Central Processing Center". The book says its street address is "123 Microsoft Way, Building 20, Floor 4". This is an **A Record**. It points a name to a physical address (an **IP Address**).
        - Now you know exactly where to go.
    - **A Record vs. CNAME Record**
        - **Feature: Points To**
            - **A Record:** An IPv4 Address.
            - **CNAME Record:** Another Domain Name.
        - **Feature: Flexibility**
            - **A Record:** **Low.** If the IP changes, you must manually update the DNS record.
            - **CNAME Record:** **High.** It automatically inherits IP changes from the target domain.
        - **Feature: Use at Apex/Root?**
            - **A Record:** **Yes.** The required method for the root domain.
            - **CNAME Record:** **No.** Violates DNS RFCs if other records exist.
        - **Feature: Typical App Service Use**
            - **A Record:** [contoso.com](http://contoso.com/)
            - **CNAME Record:** [www.contoso.com](http://www.contoso.com/), [api.contoso.com](http://api.contoso.com/)
        - **Feature: Best For**
            - **A Record:** Pointing a root domain.
            - **CNAME Record:** Pointing subdomains to PaaS services like App Service.
    - **2. Verifying Identity (The TLS/SSL Handshake and the CA)**
        - You arrive at the address. A person is sitting at the desk. How do you know this person is really Alice from the Bank of Contoso and not an imposter trying to steal your secret message?
        - You ask for her ID. She shows you her official government-issued ID card. This is her **SSL Certificate**.
        - **The Certificate Authority (CA):** The "government" that issued the ID is a trusted entity, like the DMV or Passport Office. Everyone trusts them to only issue IDs to the right people. This is the **Certificate Authority (CA)** (like DigiCert or Let's Encrypt).
        - You check her ID (the certificate):
            - **Check 1 (Domain Name):** Does the name on the ID say "Alice, Bank of Contoso"? Yes.
            - **Check 2 (Expiration):** Is the ID still valid? Yes.
            - **Check 3 (Authenticity):** Does the government seal (the CA's signature) look real and untampered with? Yes.
        - Because you trust the "government" (the CA), and the ID checks out, you now trust that this person is really Alice.
    - **3. Sharing the Secret (Encryption)**
        - You still can't just shout your secret message across the crowded post office. You need a private way to talk.
        - Alice's ID card has a special public feature: a **small, open lockbox (Public Key)**. Anyone can put a message in it and lock it, but only Alice has the **unique key (Private Key)** to open it.
        - You write down a secret code for your conversation (a "session key"), put it in her lockbox, and give it to her.
        - Alice uses her private key to open the box and get the secret code.
        - Now, both of you know the secret code, and nobody else does. You can whisper back and forth using that code for the rest of your conversation. This is the **Encrypted Session**.

---

# **How this Stops an Attacker (The Man-in-the-Middle)**

- Now, imagine an attacker, Eve, is in the post office listening.
    - When you look up the bank's address, Eve could try to shout a fake address. But DNS has its own security to help prevent this.
    - The real attack is when you arrive. Eve sits down and says, "Hi, I'm Alice!"
    - You ask for her ID. Eve has a problem. She can't steal the real Alice's ID because she doesn't have the **private key** that goes with it.
    - So, Eve shows you a fake ID she made herself.
    - Your brain (the browser) immediately notices: "This ID for 'Bank of Contoso' doesn't have a seal from a trusted government (CA) I recognize!"
    - **BOOM!** Your browser throws up a massive security warning: "This connection is not private!" The attack has failed. The trust established by the CA is the critical step that stops the imposter.

---

# **The Technical Details: How it All Connects**

- Now let's map the analogy to the technology.
    - **Part 1: How the Address Resolves ([contoso.azurewebsites.net](http://contoso.azurewebsites.net/))**
        - When you type `https://www.contoso.com` into your browser (assuming it points to an Azure App Service):
            1. **Browser:** "I need to go to `www.contoso.com`. DNS, what's the IP address?"
            2. **DNS System:** "Let me check. The record for `www.contoso.com` is a **CNAME** that points to `contoso.azurewebsites.net`."
            3. **Browser:** "Okay, new question. DNS, what's the IP address for `contoso.azurewebsites.net`?"
            4. **DNS System:** "Let me check. The record for `contoso.azurewebsites.net` is an **A Record** that points to the IP address 20.42.10.150."
            5. **Browser:** "Great. I now know the server's physical address is 20.42.10.150."
        - The DNS lookup is now complete. The browser knows where to send the request.
    - **Part 2: The TLS/SSL Handshake in Detail**
        1. **Client Hello:** Your browser connects to 20.42.10.150 and sends a message saying: "Hi, I want to establish a secure connection for the website `www.contoso.com`. Here are the encryption methods I support."
            - (This is why multiple websites can live on the same IP. The browser announces which one it's looking for).
        2. **Server Hello & Certificate:** The Azure server at that IP receives the request. It says: "Hello back. I host `www.contoso.com`. Let's use this specific encryption method. Here is my **SSL Certificate** to prove I am `www.contoso.com`."
        3. **Client Verification (Crucial Step):** Your browser examines the certificate:
            - Does the "Common Name" or "Subject Alternative Name" in the certificate match `www.contoso.com`?
            - Is the certificate's date valid (not expired)?
            - Is the certificate signed by a **Certificate Authority (CA)** that is in my browser's built-in list of trusted CAs (e.g., DigiCert, Let's Encrypt, etc.)?
        4. **Key Exchange:** If all checks pass, the browser trusts the server. It uses the **Public Key** from the certificate to encrypt a randomly generated key (the session key). It sends this encrypted key back to the server.
        5. **Secure Session Begins:** The server uses its **Private Key** (which it has kept secret and never shared) to decrypt the session key. Now, both the browser and the server have the same secret session key. They switch to a faster, symmetric encryption method using this key for all future communication. The little padlock icon appears in your browser.
    - **Summary of the Relationship:**
        - **A-Records and CNAMEs are like the address book.** They get you to the right building (the server's IP address). They have **nothing to do with the certificate itself**.
        - **The SSL Certificate is like the ID card.** You show it after you've arrived at the building to prove you are who you claim to be.
        - The connection is this: **The domain name in the DNS record you used MUST match the domain name printed inside the SSL Certificate.** If you use a CNAME for `www.contoso.com` to find the server, the server better have a certificate ready for `www.contoso.com`. If it presents a certificate for [something-else.com](http://something-else.com/), your browser will reject it, and the handshake will fail.

---

# **4. What is a Wildcard Certificate?**

- A **Wildcard Certificate** is a special type of public SSL/TLS certificate that can be used to secure an unlimited number of **first-level subdomains** under a single base domain.
- It achieves this by using an asterisk (*), known as a wildcard character, in the place of the subdomain in the "Common Name" (CN) or "Subject Alternative Name" (SAN) field of the certificate.
- For example, a wildcard certificate issued for `.contoso.com` will be trusted and valid for all of the following:
    - `www.contoso.com`
    - `api.contoso.com`
    - `shop.contoso.com`
    - `blog.contoso.com`
    - `anything-you-want.contoso.com`
    - **The Core Problem it Solves**
        - The primary problem a wildcard certificate solves is **management overhead and cost at scale**.
        - **Without a Wildcard:** For 50 subdomains, you would need to procure, install, track, and renew 50 individual certificates. This is time-consuming, expensive, and prone to human error (forgetting to renew one certificate can cause an outage for that specific service).
        - **With a Wildcard:** You manage just **one certificate**. When it's time to renew, you renew that single certificate and deploy it to all your servers. Adding a new subdomain requires no new certificate procurement.
    - **How it Works**
        - When a browser connects to `api.contoso.com`, the server presents the wildcard certificate issued for `.contoso.com`. The browser's validation logic checks:
            1. Is the certificate expired? No.
            2. Is it signed by a trusted CA? Yes.
            3. Does the requested domain (`api.contoso.com`) match the pattern in the certificate's name (`.contoso.com`)? **Yes.**
        - The validation passes, and the secure connection is established.
    - **Limitations and "Gotchas" (Very Important!)**
        - The "master key" analogy also highlights the risks.
        - **1. Does NOT Cover the Root Domain:** This is the most common misunderstanding. A certificate for `.contoso.com` **does NOT secure the root/apex domain** `contoso.com`. You would need to access `www.contoso.com` for it to be valid.
            - **Solution:** Modern Certificate Authorities solve this by issuing a **SAN (Subject Alternative Name) Certificate** that includes both `.contoso.com` and `contoso.com` as valid names. This is the standard practice today when you buy a wildcard certificate.
        - **2. Only One Subdomain Level:** The wildcard only applies to a single level. A certificate for `.contoso.com` will **NOT** work for:
            - `test.api.contoso.com` (this is a **second**level subdomain)
            - `prod.api.contoso.com`
        - **3. Security Risk: The "Compromised Master Key":** This is the biggest drawback. The private key for your wildcard certificate is incredibly sensitive. If this single private key is compromised, an attacker can impersonate and decrypt traffic for **ALL of your subdomains**. With individual certificates, a compromise is contained to just one service. Because of this, wildcard certificates demand very strict private key protection (e.g., using Azure Key Vault).
        - **4. No App Service Managed Certificate:** A key limitation within the AZ-204 context is that Azure's free **App Service Managed Certificate** feature **does not support wildcards**. To use a wildcard certificate, you must purchase one from a third-party CA and import it (preferably via Azure Key Vault).
    - **Practical Use Cases for Azure Developers**
        - **Enterprise Applications:** A large company hosts its main site (`www`), its developer portal (`developer`), its blog (`blog`), and its status page (`status`) all as separate App Services under the same domain. A single wildcard certificate can be imported into Key Vault and used by all of them.
        - **SaaS Platforms:** You're building a Software-as-a-Service product where each customer gets their own environment, like `customer-a.myapp.com` and `customer-b.myapp.com`. A wildcard certificate for `.myapp.com` allows you to instantly secure new customer environments without certificate management overhead.
        - **Development/Testing Environments:** A development team frequently spins up new feature branches for testing, such as `feature-x.dev.mycompany.com` and `feature-y.dev.mycompany.com`. A wildcard for `.dev.mycompany.com` makes this process seamless.

[Asp.net Core & SSL](DNS%20&%20SSL%20Basics/Asp%20net%20Core%20&%20SSL%202d82749a7cfe81308354e6e0b14aa9a5.md)

[**SSL Offloading & HSTS : Browser
vs API**](DNS%20&%20SSL%20Basics/SSL%20Offloading%20&%20HSTS%20Browser%20vs%20API%202d82749a7cfe81018988ceeefa4ba7fa.md)