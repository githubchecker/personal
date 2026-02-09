# ARR Affinity/Sticky Sessions

# **What is the Use of Sticky Sessions?**

**Sticky Sessions (ARR Affinity)** is a feature of the load balancer in front of your App Service Plan. Its purpose is to ensure that once a user's session is established with a specific backend server instance, all subsequent requests from that same user are directed to the **same instance** for the duration of their session.

It solves the problem of applications that store session-specific data **in the memory of the web server itself**. These are called **stateful applications**.

# **How it Works: The ARRAffinity Cookie**

1. **First Request:** A user makes their first request to your web app (`www.contoso.com`). The Azure load balancer receives it. It doesn't see any special cookie, so it uses its normal logic (e.g., round-robin) to select an available server, say **Instance B**.
2. **Response + Cookie Injection:** The request is processed by Instance B. On the way back out to the user, the load balancer intercepts the response and **injects a special cookie** into it. This cookie is named ARRAffinity and its value is a unique identifier for Instance B.
3. **Subsequent Requests:** The user's browser automatically includes this ARRAffinity cookie in all future requests to `www.contoso.com`.
4. **Affinity-Based Routing:** The load balancer now sees the incoming ARRAffinity cookie. Instead of picking a random server, it reads the cookie's value, identifies it as belonging to **Instance B**, and routes the request directly to that specific instance, bypassing its normal load-balancing logic.

This continues until the user closes their browser or the cookie expires.

# **Required Scenarios (When You Need to Use It)**

You are forced to use sticky sessions when your application is **stateful**, meaning the server code relies on data stored in its local memory to function correctly from one request to the next.

### **Example 1: The Classic In-Memory Shopping Cart**

You are running an e-commerce site built on an older framework. The shopping cart's contents are stored in the server's Session object (e.g., [ASP.NET](http://asp.net/)'s `Session["Cart"]`).

- **Request 1:** User adds a "Blue T-shirt" to their cart. This request goes to **Instance A**. The Session object in Instance A's memory now contains "Blue T-shirt".
- **Request 2 (Without Sticky Sessions):** User clicks "Checkout". The load balancer sends this request to **Instance B**. Instance B's Session object is empty. The application thinks the cart is empty, and the user sees a "Your cart is empty!" message. This is a critical failure.
- **Request 2 (With Sticky Sessions):** The ARRAffinity cookie forces the "Checkout" request back to **Instance A**. Instance A's code checks its local Session object, finds the "Blue T-shirt", and the user can proceed to checkout.

### **Example 2: A Multi-Step Online Application Form**

A user is filling out a long, 5-page wizard for an insurance quote. The data from pages 1, 2, and 3 is temporarily stored in server memory.

- When the user submits page 4, the request **must** go back to the same server instance that handled pages 1-3. Otherwise, the server processing page 4 won't know the user's name, address, or vehicle information, and the process will fail.

### **Example 3: Legacy Applications**

You are migrating a legacy on-premises application to App Service. The application was designed to run on a single server and makes heavy use of in-memory caching and session state. A full rewrite to make it stateless is not feasible due to time or budget constraints.

- In this "lift-and-shift" scenario, enabling sticky sessions is a pragmatic and necessary step to allow the application to function in a scaled-out cloud environment.

# **The Modern View: Why Sticky Sessions is Often an Anti-Pattern**

For modern cloud-native development, relying on sticky sessions is generally discouraged. The goal is to build **stateless applications**.

### **Why avoid it?**

1. **It Hinders Scalability:** If many users get "stuck" to one instance and that instance becomes overloaded with traffic or CPU usage, the load balancer can't help by distributing them to other idle instances.
2. **It Creates a Single Point of Failure:** If the instance a user is stuck to crashes, is rebooted, or is taken down for deployment, their session is completely lost. Their shopping cart is emptied, or they are logged out.
3. **It Complicates Deployments:** It makes zero-downtime deployments more complex to manage.

### **The Stateless Alternative:**

The best practice is to **externalize your state**. Instead of storing session data in the web server's memory, store it in a centralized location that all your server instances can access.

- **Azure Cache for Redis:** A high-performance, distributed cache. Instead of `Session["Cart"]`, you'd write `redis.Set("user123_cart", cartData)`. Now, any instance (A, B, or C) can handle the user's request because they can all connect to the same Redis cache to retrieve the cart data.

By designing your app this way, you can **turn sticky sessions off**. The load balancer is free to distribute traffic to any available instance, which is more resilient, more scalable, and better for reliability.