# Keys in KeyValue

This is a fundamental concept in modern computing, yet it is where most mistakes happen. As your Principal Architect, I will strip away the complex math and explain this strictly in terms of **Software Architecture and Azure Key Vault Mechanics**.

We are discussing **Asymmetric Cryptography** (RSA).

---

### **Section 1: The Concept (The Lock & The Key)**

To understand the use case, you must understand the rules of the two keys.

### **1. The Public Key (The "Padlock")**

- **What is it?** A string of data that you can post on your website, email to everyone, or put on a billboard. It is **Not Secret**.
- **Function:** It is used **ONLY to Encrypt** (Lock) data.
- **Analogy:** Think of the Public Key as an **open padlock**. You can give padlocks to anyone. They put their message in a box, use your padlock to lock it, and send the locked box to you.
- *Crucially:* Once they lock it, **even they cannot open it again.**

### **2. The Private Key (The "Master Key")**

- **What is it?** A secret cryptographic sequence generated inside the Azure Key Vault.
- **Function:** It is used **ONLY to Decrypt** (Unlock) data.
- **Analogy:** You are the only person in the world who has the key to open those padlocks.
- *Security:* If you lose this key, the data in the box is gone forever. If you share this key, anyone can read your secrets.

### **The "Real World" Use Case: Secure Data Submission**

Imagine you are building a banking API.

1. **Client (Mobile App/Browser):** The user enters their Social Security Number (SSN). You don't want to send this as plain text. The Mobile App has your **Public Key** embedded in it. The App encrypts the SSN locally.
2. **Transport:** The "Ciphertext" (scrambled SSN) is sent over the internet. If a hacker intercepts it, they only see garbage.
3. **Server (Your C# API):** Your API receives the garbage data. Your API connects to **Azure Key Vault** (which holds the **Private Key**) to decrypt it and get the real SSN.

---

### **Section 2: Implementation Details**

Here is the full lifecycle code.

### **Part A: The Sender (The Client)**

- *Note:* The sender does **not** need Azure Key Vault permissions. They just need the Public Key string (RSA parameters).

```csharp
using System.Security.Cryptography;
using System.Text;

public string ClientSideEncryption(string sensitiveData, string publicKeyXml)
{
    // 1. Create a local RSA instance
    using (RSA rsa = RSA.Create())
    {
        // 2. Import the PUBLIC Key (Safe to have in frontend code)
        rsa.FromXmlString(publicKeyXml); // In .NET Core/5+ we often use ImportSubjectPublicKeyInfo

        byte[] dataToEncrypt = Encoding.UTF8.GetBytes(sensitiveData);

        // 3. Encrypt using OAEP padding (Standard for security)
        // Notice: We only need the Public key to do this.
        byte[] encryptedData = rsa.Encrypt(dataToEncrypt, RSAEncryptionPadding.OaepSHA256);

        // Return Base64 string to send to API
        return Convert.ToBase64String(encryptedData);
    }
}

```

### **Part B: The Receiver (Your API with Azure Key Vault)**

- *Note:* This code runs on your secure server. It uses the **Private Key** stored in Azure.

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Keys.Cryptography;
using System.Text;

public class DecryptionService
{
    private readonly CryptographyClient _cryptoClient;

    public DecryptionService(string keyId)
    {
        // "keyId" looks like: <https://my-vault.vault.azure.net/keys/MyRsaKey/CURRENT_VERSION_GUID>
        // This client authenticates using your Server's Managed Identity
        _cryptoClient = new CryptographyClient(new Uri(keyId), new DefaultAzureCredential());
    }

    public async Task<string> ServerSideDecryptionAsync(string encryptedBase64)
    {
        byte[] ciphertext = Convert.FromBase64String(encryptedBase64);

        // 1. Send the scrambled data to Azure Key Vault
        // The Vault uses the PRIVATE KEY (which never leaves the hardware) to do the math.
        DecryptResult result = await _cryptoClient.DecryptAsync(EncryptionAlgorithm.RsaOaep256, ciphertext);

        // 2. We get back the raw bytes (Plain Text)
        return Encoding.UTF8.GetString(result.Plaintext);
    }
}

```

---

### **Section 3: Mechanics & Rules (The Deep Dive)**

How does this work "Under the Hood" without exposing the secret?

### **1. The One-Way Trip (Trapdoor Function)**

The mathematics behind RSA involves multiplying two massive prime numbers.

- **Public Key Action:** It's easy to multiply two numbers to get a result (Encryption).
- **Private Key Action:** It's incredibly hard to factor that result back into original numbers *unless* you already know one of the factors. The **Private Key** is that factor.
- **Azure's Role:** Azure generates both keys inside the Hardware Security Module (HSM). It gives you the Public Key to download. It **buries** the Private Key deep in silicon.

### **2. Dispatch & Memory Layout**

When you call `DecryptAsync` in your C# API:

1. **Stack:** Your API holds the `ciphertext` (random garbage bytes) on the Stack/Heap.
2. **Network:** Your API serializes this garbage into a JSON payload and HTTPS POSTs it to Azure.
3. **The Vault:**
    - Authenticates your API (Entra ID).
    - Loads the Private Key into the HSM processor registers.
    - Injects your ciphertext into the processor.
    - The processor outputs the Plain Text.
4. **Return:** Azure sends the Plain Text back to your API over the network.
5. **Heap:** The plain text string finally appears in your API's memory.

**CRITICAL ARCHITECTURE NOTE:** The Private Key never existed in your API's memory. Even if a hacker dumps your API's RAM, they won't find the Private Key. They will only find the one specific message you just decrypted.

---

### **Section 4: Best Practices & Decision Matrix**

### **Good Patterns**

- **Key Rotation:** Since you distribute the Public Key to clients, if you rotate (change) the Key Pair in Azure, the clients will stop working because they are encrypting with the *old* Lock, but you are trying to open with the *new* Master Key.
    - *Solution:* Architect a way for clients to fetch the latest Public Key on startup.
- **Use OAEP Padding:** In the code `RSAEncryptionPadding.OaepSHA256`. Do not use `Pkcs1`. Old padding schemes have mathematical vulnerabilities.

### **When to use Asymmetric (Public/Private) Decryption?**

| Scenario | Strategy | Why? |
| --- | --- | --- |
| **Sending Passwords/Credit Cards to API** | **USE THIS** | The client encrypts (Public), only Server sees data (Private). Perfect. |
| **Storing Data in Database** | **DO NOT USE** | Asymmetric is slow and creates huge data bloat. Use Symmetric (AES) for storage. |
| **Encrypting > 190 bytes of data** | **DO NOT USE** | RSA keys have a size limit. Use "Hybrid Encryption" (Encrypt an AES key with RSA, then data with AES). |

---

### **Section 5: Important Notes & Gotchas**

- **The Size Limit:** A standard 2048-bit RSA key can only encrypt roughly **190 bytes** of data (about a short paragraph). If you try to encrypt a PDF file or a long JSON string, the code will throw a `CryptographyException: Message too long`.
    - *Fix:* Use the Hybrid/Envelope approach discussed in the previous section.
- **Performance:** Decryption with a Private Key in Key Vault is a **remote network call**. It takes ~15ms - 50ms.
    - *Warning:* Do not decrypt 10,000 items in a `foreach` loop. Your application will hang.
- **Reversibility:** Encryption is meant to be reversed (Decrypted). Hashing (like SHA256 for passwords) is *not* reversible. Do not confuse the two. You use RSA Key Vault keys when you need the original data back (e.g., Credit Card number to process a payment).

# We will focus on the **single most important pattern** you will use as a C# developer: **"Envelope Encryption"**

### **Section 1: The Concept (The "Digital Locker" Analogy)**

Think of it like this:

1. **The Data (Gold Bar):** Your huge PDF file or database column. It is too big/heavy to send to Azure for encryption.
2. **The Local Key (Small Padlock):** You generate a fast, temporary key (AES) on your server. You lock the Gold Bar with this Small Padlock.
3. **The Master Key (Bank Vault):** The Master Key lives inside Azure Key Vault. It is huge and immovable.
4. **The Process:**
    - You lock the Data with the Local Key.
    - You send **ONLY** the Local Key to Azure.
    - Azure locks your Local Key inside the Bank Vault and sends it back.
    - You save the **"Locked Local Key"** next to your data.

---

### **Section 2: Implementation Details (The Easy Way)**

We use the library **`Azure.Security.KeyVault.Keys`**.

### **Step 1: The Setup (Connecting)**

This happens once in your `Program.cs` or Service Constructor.

```csharp
using Azure.Identity; // For Authentication
using Azure.Security.KeyVault.Keys; // For Managing Keys
using Azure.Security.KeyVault.Keys.Cryptography; // For DOING crypto

// 1. The URL of the Specific Master Key in Azure
// Format: https://{vault-name}.vault.azure.net/keys/{key-name}
Uri keyId = new Uri("<https://my-secure-vault.vault.azure.net/keys/MasterKey>");

// 2. The Client
// This client knows how to talk to that specific Key to do math.
var cryptoClient = new CryptographyClient(keyId, new DefaultAzureCredential());

```

### **Step 2: The "Lock" Process (Encryption)**

You have a temporary password (AES key) that protects your data. You want to protect that password using Azure.

```csharp
public async Task<byte[]> ProtectMyPasswordAsync(byte[] localKeyParams)
{
    // localKeyParams = The raw bytes of your temporary AES key.

    // 3. Ask Azure to "Wrap" (Encrypt) this small key
    // We use "RSA-OAEP" because it is the industry standard for safety.
    WrapResult result = await cryptoClient.WrapKeyAsync(
        KeyWrapAlgorithm.RsaOaep,
        localKeyParams
    );

    // 4. Return the ENCRYPTED key.
    // This is safe to save in your SQL Database. It looks like random garbage.
    return result.EncryptedKey;
}

```

### **Step 3: The "Unlock" Process (Decryption)**

You pull the "Garbage" from the database, and you need the real password back to open your data.

```csharp
public async Task<byte[]> RevealMyPasswordAsync(byte[] encryptedKeyFromDb)
{
    // encryptedKeyFromDb = The random garbage you saved earlier.

    // 5. Ask Azure to "Unwrap" (Decrypt) the key
    // Azure checks your identity. If allowed, it uses the Private Key in the HSM.
    UnwrapResult result = await cryptoClient.UnwrapKeyAsync(
        KeyWrapAlgorithm.RsaOaep,
        encryptedKeyFromDb
    );

    // 6. Return the RAW key.
    // Now you have the clean password back in memory to unlock your data.
    return result.Key;
}

```

---

### **Section 3: Mechanics & Rules (The Deep Dive)**

Why do we do it this way?

### **1. The Performance Rule**

- **Problem:** If you sent your 50MB video file to Key Vault to encrypt, it would fail (max size limit ~190 bytes) and be incredibly slow.
- **Mechanic:** That is why we use **WrapKey**. We only send 32 bytes (the size of a standard AES Key) over the network. It is lightning fast.

### **2. Memory Layout (Stack vs Heap)**

- When you call `UnwrapKeyAsync`, the **Raw Key** comes back and lives on the **Managed Heap** (in memory).
- **Security Warning:** As soon as you are done using that key to unlock your data, you should let it go out of scope so the Garbage Collector (GC) can clean it up. Don't store it in a `static` variable!

### **3. Network Trip**

- Every time you call `Wrap` or `Unwrap`, your application makes an HTTPS request to Azure.
- **Latency:** It takes about 20-50 milliseconds.
- **Cost:** You pay Azure roughly $0.03 per 10,000 requests.

---

### **Section 4: Best Practices**

- **Cache the Client:** Do not create `new CryptographyClient` for every single request. Create it once (Singleton) and reuse it. The client is thread-safe.
- **Handling Errors:** Always wrap the calls in a `try/catch`. If the Key in Azure is deleted or disabled, the code will throw a `RequestFailedException`.
    
    ```csharp
    try {
        await cryptoClient.UnwrapKeyAsync(...);
    }
    catch (RequestFailedException ex) {
        // Log "Key not found or Access Denied"
    }
    
    ```
    

---

### **Section 5: Important Notes**

- **Prerequisite:** You must have the specific Key created in Azure Key Vault *before* you run this code. This code assumes a key named "MasterKey" already exists.
- **Permissions:** Your app needs the **"Key User"** role (specifically `Wrap Key` and `Unwrap Key` permissions) to make this work. Reader access is not enough.

# Full Example

---

### **Section 1: The Concept (What & Why)**

- **Definition:** While a **Secret** is a simple blob of text (like a password) that you fetch and use, a **Key** is a complex cryptographic object (RSA or Elliptic Curve).
    - **Crucial Distinction:** You almost never "download" the Private Key to your C# app. Instead, you send data *to* the Key Vault, it performs the math (Encryption/Signing) inside the Vault, and returns the result. The Private Key never leaves the Azure infrastructure.
- **The "Real World" Check:**
    - **The Scenario:** You need to encrypt Credit Card numbers (PII) in your SQL Database.
    - **Bad Pattern:** You create a static string `AES_KEY = "Sup3rS3cr3t"` in your C# code to encrypt the data. If the hacker gets your DLL, they get the key and all the credit cards.
    - **The Architect's Pattern ("Envelope Encryption"):** You generate a unique AES key in memory for the data. Then, you ask Key Vault to **Encrypt (Wrap)** that AES key using the Master RSA Key stored in the Vault. You store the encrypted AES key in the database alongside the credit card data.
    - **Result:** Even if the database *and* the code are stolen, the data is useless because the Master Key is locked safely inside the Azure HSM (Hardware Security Module).

---

### **Section 2: Implementation Details**

We need two libraries:

1. **`Azure.Security.KeyVault.Keys`**: To create and manage keys.
2. **`Azure.Security.KeyVault.Keys.Cryptography`**: To actually Perform operations (Encrypt, Sign, Verify).

### **Scenario A: Creating a Key (The Setup)**

This is typically done by DevOps or via a setup script, but here is the C# control code.

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Keys;

// 1. Management Client
var keyClient = new KeyClient(new Uri("<https://my-vault.vault.azure.net/>"), new DefaultAzureCredential());

// 2. Create an RSA Key
// We use RSA because it can both Encrypt and Sign.
var options = new CreateKeyOptions("MasterEncryptionKey", KeyType.Rsa)
{
    KeySize = 2048 // Standard balance of security/speed
};

KeyVaultKey key = await keyClient.CreateKeyAsync(options);
Console.WriteLine($"Key ID: {key.Id}"); // Useful for configuring the CryptographyClient

```

### **Scenario B: Envelope Encryption (The Daily Driver)**

This is how your API code protects data. It "Wraps" (encrypts) a local symmetric key.

```csharp
using Azure.Identity;
using Azure.Security.KeyVault.Keys.Cryptography;

public class EncryptionService
{
    private readonly CryptographyClient _cryptoClient;

    public EncryptionService(string keyId) // keyId from the step above
    {
        // We connect specifically to the KEY, not just the vault
        _cryptoClient = new CryptographyClient(new Uri(keyId), new DefaultAzureCredential());
    }

    public async Task<byte[]> ProtectLocalKeyAsync(byte[] localAesKey)
    {
        // 1. Request Key Vault to "Wrap" (Encrypt) our local key
        // We use RSA-OAEP: Optimal Asymmetric Encryption Padding (Industry Standard)
        WrapResult result = await _cryptoClient.WrapKeyAsync(KeyWrapAlgorithm.RsaOaep, localAesKey);

        // 2. This returned byte array is now safe to store in SQL/CosmosDB
        // It can only be decrypted by the Key Vault itself.
        return result.EncryptedKey;
    }

    public async Task<byte[]> UnprotectLocalKeyAsync(byte[] encryptedKey)
    {
        // 1. Send the blob back to AKV to decrypt
        UnwrapResult result = await _cryptoClient.UnwrapKeyAsync(KeyWrapAlgorithm.RsaOaep, encryptedKey);

        // 2. result.Key is the raw AES key to use in memory
        return result.Key;
    }
}

```

---