# Phase 7: Monitoring & Troubleshooting

This is the most "hands-on" phase. When you move to AKS, you lose the ability to RDP into a server, open Task Manager, or view Event Viewer.

You must relearn how to observe your application using **Signals** (Probes) and **Telemetry** (Container Insights).

---

### **1. Probes (Teaching K8s how to fix your app)**

Kubernetes has a feature called "Self-Healing." If a Pod crashes, it restarts it.
But what if the Pod is "running" (Process ID exists) but is stuck in a deadlock or is disconnected from the database? To K8s, it looks healthy.

You must fix this using **Probes**.

### **A. The Three Types of Probes**

1. **Startup Probe:** "Are you alive yet?"
    - **Scenario:** Your .NET app takes 30 seconds to warm up caches.
    - **Behavior:** K8s will **wait** before doing anything else. If this fails after X seconds, K8s kills the pod and retries.
2. **Liveness Probe:** "Should I kill you?"
    - **Scenario:** Your app deadlocked. Memory is high, but the CPU is idle.
    - **Behavior:** If this endpoint fails, K8s **Restarts** the container (Delete -> Recreate).
3. **Readiness Probe:** "Should I send you traffic?"
    - **Scenario:** Your app is fine, but the SQL Database is temporarily down. You can't process requests.
    - **Behavior:** If this fails, K8s does **NOT** kill the pod. It simply removes the Pod from the **Service (Load Balancer)**. Traffic stops hitting this specific Pod until it recovers.

### **B. The .NET Implementation**

**C# Code (`Program.cs`):**
Use the native Health Checks library to expose endpoints.

```csharp
builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy()) // For Liveness
    .AddSqlServer(connectionString); // For Readiness (Dependent Service)

// ...

app.MapHealthChecks("/health/live", new HealthCheckOptions { Predicate = r => r.Name.Contains("self") });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = r => r.Tags.Contains("sql") });

```

**YAML Configuration:**

```yaml
spec:
  containers:
  - name: my-api
    # ...
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10

```

---

### **2. Container Insights (Where are my logs?)**

In the old days, you wrote to `C:\\logs\\app.txt`. In containers, **Filesystems are temporary.** If you write to a file, it disappears when the Pod moves.

**The "12-Factor App" Rule:**
Logs are a stream. **Always write to Standard Output (Console).**

**The Architecture:**

1. **You:** `Console.WriteLine("User Logged In");`
2. **Docker:** Captures that line to a JSON file on the Node.
3. **Azure Monitor Agent:** A DaemonSet (Agent) running on every Node reads that JSON file.
4. **Log Analytics Workspace:** The Agent pushes the logs to Azure.

### **Querying Logs (KQL)**

Go to Azure Portal -> AKS -> Logs. We use **Kusto Query Language (KQL)**.

**Novice Query:** "Show me everything" (Don't do this, it's expensive).

```
ContainerLog
| where TimeGenerated > ago(1h)

```

**Expert Query:** "Show me Exceptions in my OrderService."

```
ContainerLog
| where ContainerName == "order-service"
| where LogEntry contains "Exception"
| project TimeGenerated, LogEntry, PodName
| order by TimeGenerated desc

```

---

### **3. The "Why is it broken?" Toolbelt (`kubectl`)**

When a deployment fails, use these 4 commands in order.

### **1. `kubectl get pods`**

**Status check.**

- `Running`: Good.
- `Pending`: Bad. usually means **No Nodes available** (Cluster full) or **PVC Missing**.
- `CrashLoopBackOff`: Bad. The app started, crashed, restarted, and crashed again.
- `ImagePullBackOff`: Bad. Wrong Image Name or Authentication failed (ACR Secret missing).

### **2. `kubectl describe pod [name]`**

**The "Event Log".** This tells you *what K8s tried to do*.

- *Output:* "Failed to pull image..."
- *Output:* "0/3 nodes are available: 3 Insufficient cpu." (Need to scale up).
- *Output:* "Readiness probe failed: Get http://.../health: 500."

### **3. `kubectl logs [name]`**

**The "Application Log".** Use this for `CrashLoopBackOff`.

- It prints the last ~50 lines of Console Output.
- *Common .NET error:* `Unhandled Exception: System.Data.SqlClient.SqlException...` (Shows you connection string is wrong).
- *Live tailing:* `kubectl logs -f [name]` (Follow mode).

### **4. `kubectl exec -it [name] -- sh`**

**The "SSH" equivalent.** This drops you inside the running container.

- **Use case:** Debugging networking.
- *Scenario:* "Why can't I reach the database?"
- *Action:* `exec` into the pod and run `curl <http://db-service`>. If that fails, it's a Cluster Network issue, not a C# issue.

---

### **4. Common Crash Scenarios (Expert Diagnosis)**

### **Scenario A: OOMKilled (Out of Memory)**

- **Symptom:** Pod restarts. `kubectl get pods` shows `Restarts: 5`. `kubectl describe` says `Reason: OOMKilled`.
- **Cause:** Your container tried to use 513MB of RAM, but YAML `limits.memory` was `512Mi`. Linux Kernel killed it.
- **Fix:** Increase the Limit in YAML, or fix the Memory Leak in C#.

### **Scenario B: CrashLoopBackOff**

- **Symptom:** Status starts as `Running`, waits 2 seconds, changes to `Error`, then `CrashLoopBackOff`.
- **Cause:** The application threw an exception during `Startup.cs` or `Program.cs`.
    - Missing `appsettings.json` Config.
    - Database connection failed immediately.
- **Fix:** `kubectl logs [podname]` (You typically check the **Previous** instance: `kubectl logs [podname] --previous`).

### **Scenario C: 504 Gateway Time-out**

- **Symptom:** You hit `api.com` and get 504.
- **Cause:** The Request hit the Ingress, Ingress forwarded to Service, Service forwarded to Pod, but **Pod didn't answer**.
- **Fix:** Check if CPU usage is hitting the Limit (Throttling). Check if thread pool is exhausted (C# code issue).

---

### **Final Expert Skill: `dotnet-monitor`**

In the old days, if an app was slow, you took a **Memory Dump**. In K8s, how do you dump memory on a container that runs on a stripped-down Linux kernel?

**The Sidecar Approach:**
You run a specialized container called `dotnet-monitor` alongside your API in the same Pod.

- It shares the "Process Namespace".
- You call an API on the sidecar: `curl <http://localhost:52323/dump`>.
- It grabs the memory dump of the *Main* API container and streams it to Blob Storage.

---

### **Conclusion of the Kubernetes Masterclass**

You have navigated from understanding the **Control Plane** (Phase 1) to writing **Deployment YAML** (Phase 2), exposing it via **Ingress** (Phase 3), injecting **Workload Identity** (Phase 4), managing **Persistence** (Phase 5), optimizing **Autoscaling** (Phase 6), and finally **Debugging** crashes (Phase 8).

**Your path to Expert is now built on:**

1. **Architecture:** Azure Manages the Master; You manage the Nodes.
2. **Manifests:** YAML is your source code. Version control it.
3. **Statelessness:** Pets vs Cattle. Treat pods like cattle.
4. **Observability:** If it's not in StdOut (Console), it didn't happen.

**Do you have any final questions on this entire Azure/Docker/Kubernetes journey?**