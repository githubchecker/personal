# Custom Auto Scale

This is an outstanding question that cuts right to the heart of the Azure platform's hosting models. You are correctly identifying that while Azure Functions are "serverless" in concept, their underlying execution model changes dramatically depending on the plan you choose.

Let's break this down completely.

# **How an Azure Function Works on an App Service Plan**

First, let's establish the model. When you run a Function App on an **App Service Plan**, you are essentially treating it like a specialized Web App.

- **You Lose "Serverless" Scaling:** You are no longer in the pay-per-execution, scale-from-zero "serverless" world of the Consumption plan.
- **You Gain Predictable Resources:** You are paying a fixed hourly rate for the App Service Plan's underlying VM instances, whether your function runs once or a million times. The resources (CPU/RAM) are dedicated to your plan.
- **The Runtime is "Always On":** Unlike a Consumption plan function that goes to sleep, a function on an App Service Plan runs continuously on the provisioned instances. The Function Host runtime is always running, actively listening for triggers.

Think of it this way: In a **Consumption Plan**, Azure is the event manager who sees a guest arrive (a message on a queue) and quickly spins up a waiter (a function instance) to serve them, then sends the waiter home. In an **App Service Plan**, you've hired one or more waiters (instances) to stand around in the kitchen 24/7, ready to act the moment a guest arrives.

### **The Critical Setting: "Always On"**

For a Function App to work correctly on an App Service Plan, you **must** enable the **"Always On"** setting in the App Service configuration. If this is turned off, after a period of inactivity, the App Service Plan will idle your site. This would shut down the Function Host runtime, and your triggers (like queue or timer triggers) would stop firing. "Always On" ensures your code is always loaded and ready.

---

# **How Autoscale Affects the Co-Hosted Function App**

This is the central part of your question. Let's use the same scenario:

- **App Service Plan:** 1 instance (S1 tier)
- **Apps in the Plan:**
    1. A public-facing **Web App**
    2. A background processing **Function App** (e.g., listening to a Service Bus queue)

**Scenario: The Web App triggers a scale-out.**

1. **Trigger:** The Web App gets a massive traffic spike, pushing the App Service Plan's total CPU usage to over 80%.
2. **Autoscale Rule Fires:** The plan's autoscale rule ("add an instance if CPU > 70%") is triggered.
3. **Azure Action:** Azure provisions a second VM instance (**Instance 2**).
4. **Replication:** Just like before, this new instance gets a full copy of the entire plan's configuration. This means:
    - A copy of the **Web App** is deployed and started on Instance 2.
    - A copy of the **Function App** is also deployed on Instance 2, and its Function Host runtime also starts up.

### **The Direct Effect on the Azure Function:**

You now have **two** independent Function Host runtimes active, both belonging to the same Function App.

- **Instance 1:** Function Host is running and listening for triggers.
- **Instance 2:** A new Function Host is also running and listening for the exact same triggers.

**How do the triggers behave now?**

- **Timer Trigger ([TimerTrigger]):** Azure is smart enough to ensure that a singleton timer trigger only runs on **one** of the instances at a time. It uses a distributed lock mechanism behind the scenes to prevent it from firing on all instances simultaneously.
- **Queue / Service Bus Triggers ([QueueTrigger], [ServiceBusTrigger]):** This is the most interesting case. Both instances will now start actively polling the same queue. This creates a **"competing consumer"** pattern. The two instances will now work **in parallel** to process messages from the queue. Instance 1 will grab a message and process it, and at the same time, Instance 2 can grab another message and process it. This **effectively doubles your message processing throughput**. The underlying Function SDKs handle the message leasing to ensure the same message is not processed by both instances.

---

# **The Big Problem: Mismatched Scaling Logic**

Here is the architectural flaw in this shared plan model, which you are right to question:

Your **Function App's workload** is likely driven by the number of messages in the queue. You want it to scale out when the queue length is high and scale in when it's empty.

Your **App Service Plan's autoscaling** is configured to scale based on **CPU or Memory**.

**These two things have no direct relationship.**

- **Negative Scenario 1 (Web App causes unneeded scaling):** The Web App's high CPU usage scales you out to 5 instances. Now you have 5 Function App instances polling a nearly empty queue, and you are paying 5x the cost for no reason.
- **Negative Scenario 2 (Function App needs to scale but can't):** 100,000 messages are suddenly dumped into your queue. The processing for each message is very lightweight and not CPU-intensive. Your Function App is overwhelmed and falling behind, but because the total plan CPU is low (the Web App is idle), **the autoscale rule never fires**. Your Function App is starved of resources precisely when it needs them most.

# **Best Practice and Conclusion**

For any serious application, you should **isolate your Function App into its own dedicated hosting plan** that is appropriate for its workload.

1. **For spiky, unpredictable workloads:** Put the Function App in a **Consumption Plan**. It will scale from 0 to N instances based on the number of incoming events (e.g., queue messages), which is the exact logic you want.
2. **For high-throughput, constant workloads needing VNet integration:** Put the Function App in a **Premium Plan** or its **own dedicated App Service Plan**. A dedicated App Service Plan allows you to set autoscale rules that make sense for the function's workload (e.g., scale based on queue length using Azure Monitor metrics).

Putting a Web App and a non-trivial Function App in the same App Service Plan is generally an anti-pattern because of the "noisy neighbor" problem and, more critically, the **mismatched scaling logic**.