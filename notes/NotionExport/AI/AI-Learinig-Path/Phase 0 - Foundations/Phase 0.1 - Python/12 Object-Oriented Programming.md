# 12 — Object-Oriented Programming (OOP)

> Phase 0 · Module 0.1 · Lesson 12 of 16

## 🗺️ Stage 0 — Concept Map

So far you've used data (lists, dicts) and behaviour (functions) separately. **OOP** bundles them
together: a **class** packages related data *and* the functions that work on it into one reusable
type. You'll mostly *use* classes that libraries provide (a `SentenceTransformer`, an `OpenAI`
client, a Pydantic `BaseModel`), so understanding how they work makes every library click.

## 🔑 New Terms (plain English)

- **Class** — a blueprint for making objects.
- **Object / instance** — a specific thing built from a class.
- **`__new__`** — the allocator method; runs *before* `__init__` to allocate raw heap memory. Receives `cls` and returns the new instance.
- **`__init__`** — the initializer method; Python calls it automatically immediately after `__new__` to set up initial state. Receives `self` and returns `None`.
- **Singleton** — a design pattern ensuring only one instance of a class exists in memory.
- **`self`** — the current instance, inside a method (a strict convention, not a reserved keyword).
- **Class attribute** — data shared by all instances of a class (acts like a shared static variable; trap if mutable!).
- **`_variable` (Protected by convention)** — single leading underscore signals internal use (accessible, but hands-off by convention).
- **`__variable` (Private / name mangling)** — double leading underscores trigger Python name mangling (`_Class__var`) to prevent subclass collisions.
- **`@property` (Getter / Setter / Deleter)** — decorator that turns methods into attribute access with validation and cleanup.
- **`@classmethod`** — a method receiving the class (`cls`) instead of `self`; Python's standard way to build alternative constructors.
- **`@staticmethod`** — a plain function namespaced inside a class; receives neither `self` nor `cls`.
- **Inheritance** — a class building on another; **dunder** — special `__methods__` Python calls for you.
- **`self.__dict__`** — internal dictionary mapping attribute names to their values for an instance.
- **`__eq__`** — dunder method defining equality (`==`); defaults to identity (`is`) unless overridden.
- **`ABC` & `@abstractmethod`** — Abstract Base Class; defines an interface contract that cannot be instantiated until subclasses implement all required methods and properties.
- **`Enum` (Enumeration)** — a symbolic set of named constant values; prevents invalid string bugs and provides type-safe options.
- **`Protocol` (`typing.Protocol`)** — structural subtyping (static duck typing); defines an interface contract satisfied by any class with matching methods/attributes without inheritance.
- **Ellipsis (`...`)** — built-in singleton used idiomatically as the body of Protocol method signatures to mark an intentionally empty definition.
- **`@runtime_checkable`** — decorator enabling `isinstance()` checks against a `Protocol` at runtime (checks attribute existence).

## 🎈 Stage 1 — The Simple Idea (analogy: a cookie cutter and cookies)

A **class** is a cookie cutter — a blueprint that defines a shape. An **object** (or **instance**)
is an actual cookie stamped from it. One cutter, many cookies, each with its own decorations. The
class says *what every dog has* (a name, a `bark()` ability); each dog object fills in its own
details.

**The "Aha!":** a class defines a new **type** that carries both **state** (its data, called
attributes) and **behaviour** (its functions, called methods) together.

## ⚙️ Stage 2 — How It Actually Works

### 12.1 Defining a class

```python
class Dog:
    def __init__(self, name, age):   # __init__ runs when you CREATE an instance ("constructor")
        self.name = name             # "self" is THIS particular dog; store its data on it
        self.age = age               # these are INSTANCE ATTRIBUTES (per-object state)

    def bark(self):                  # a METHOD: a function that belongs to the class
        return f"{self.name} says woof!"

# Create instances (each is its own object with its own data):
rex = Dog("Rex", 3)        # __init__ runs with name="Rex", age=3
fido = Dog("Fido", 5)
print(rex.name)            # 'Rex'   — access an attribute
print(rex.bark())          # 'Rex says woof!'   — call a method
print(fido.bark())         # 'Fido says woof!'
```

`self` is the first parameter of every method — it's the specific instance the method was called
on. You never pass it explicitly; Python supplies it (`rex.bark()` → `bark(rex)`).

> [!NOTE]
> **Is `self` a hardcoded keyword?**
> No! `self` is **not a reserved keyword** in Python. Python simply passes the current instance as the first argument to any instance method. You could technically name this first parameter `this`, `me`, or anything else, and Python would execute it without error. However, naming it **`self` is the universal, non-negotiable community standard (PEP 8)**. Using anything other than `self` breaks linters, code completion, and developer readability—so always stick to `self`.

#### 🔍 Under the Hood: When and How Python Calls `__init__`

What actually happens behind the scenes when you write `rex = Dog("Rex", 3)`?

Python executes a **two-phase creation sequence**:

1. **Step 1: Allocation (`__new__`)**  
   Python first calls `Dog.__new__(Dog, "Rex", 3)` to allocate the raw, uninitialized object in memory. This is the true creator/memory allocator.
2. **Step 2: Initialization (`__init__`)**  
   Once the empty object exists in memory, Python **automatically** passes it as the first argument (`self`) to `__init__(self, "Rex", 3)` to attach its initial data (`self.name = "Rex"`, `self.age = 3`).

```
   Dog("Rex", 3)
         │
         ▼
 1. Dog.__new__(Dog)    ──>  Allocates raw empty object in memory
         │
         ▼
 2. Dog.__init__(self)  ──>  Initializes attributes: self.name = "Rex", self.age = 3
         │
         ▼
  Returns the initialized instance (rex)
```

**Key rules to remember about `__init__`:**
* **Automatic, immediate execution:** You never call `rex.__init__(...)` yourself. Every single line of code inside `__init__` (prints, math, input validation) runs synchronously from top to bottom the moment you write `Dog(...)`.
* **It must return `None`:** `__init__` is an *initializer*, not a factory function. Python automatically returns the new instance for you. If you attempt to write `return self` or `return some_value`, Python raises:
  `TypeError: __init__() should return None, not '...'`
* **What if you omit `__init__`?** If you don't define `__init__`, Python uses a default parameterless one inherited from the base `object` class (`d = Dog()` works, but creates an instance without custom initial attributes).

##### 🔬 Deep Dive: `__new__` vs. `__init__` (How `super().__new__` Works & The Singleton Pattern)

To understand Python's object creation at an architectural level, compare their core responsibilities:

| Feature | `__new__(cls, ...)` | `__init__(self, ...)` |
| :--- | :--- | :--- |
| **Primary Role** | **Allocator / Creator** (Allocates heap memory for the instance) | **Initializer** (Attaches data & attributes to the instance) |
| **First Parameter** | `cls` (the class itself) | `self` (the newly allocated instance) |
| **Return Value** | **MUST return an instance** (typically from `super().__new__(cls)`) | **MUST return `None`** (raises `TypeError` if you return a value) |
| **Execution Order** | Runs **1st** (before the instance exists) | Runs **2nd** (only if `__new__` returns an instance of `cls`) |
| **When to Override** | Singletons, caching, immutable types (`int`/`tuple` subclasses) | Almost every custom class |

###### How `super().__new__(cls)` Works Even With No Parent Class

You will frequently see `__new__` written like this:
```python
class Connection:
    def __new__(cls, *args, **kwargs):
        # How does super() work if Connection has no parent class in parentheses?
        instance = super().__new__(cls)
        return instance
```

**The Mystery:** Where does `super()` resolve if `Connection` didn't specify any parent?

**The Solution:** In Python 3, **every class implicitly inherits from `object`**!  
Writing `class Connection:` is 100% identical under the hood to writing `class Connection(object):`.

* Python's universal root class `object` provides the built-in allocator method: `object.__new__(cls)`.
* When you call `super().__new__(cls)`, Python's Method Resolution Order (MRO) resolves straight to `object.__new__(cls)`.
* `object.__new__(cls)` is implemented directly in C inside the CPython runtime. It allocates a block of heap memory and sets its internal type pointer to `cls`.
* By passing `cls` to `super().__new__(cls)`, you tell Python's root allocator: *"Allocate raw memory for an instance of `cls` and return it."*

###### Practical Real-World Example: The Singleton `Connection` Pattern

A **Singleton** guarantees that a class has **only one single instance in memory** across your entire application (e.g. sharing an expensive database connection pool, API client, or LLM weights).

```python
class DatabaseConnection:
    # Class attribute to store the one single instance in memory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        # 1. If no instance exists yet, allocate it via Python's root allocator:
        if cls._instance is None:
            print("[__new__]: No instance found. Allocating memory via super().__new__(cls)...")
            cls._instance = super().__new__(cls)
        else:
            print("[__new__]: Existing instance found. Returning cached instance...")
        
        # 2. Return the single instance:
        return cls._instance

    def __init__(self, db_url: str):
        # ⚠️ CRITICAL GOTCHA: The Singleton __init__ Trap!
        # Python automatically calls __init__ EVERY TIME you write DatabaseConnection(...),
        # even when __new__ returns an existing, cached instance!
        # Without a guard flag, subsequent calls will overwrite your singleton's state:
        if not hasattr(self, "_initialized"):
            print(f"[__init__]: Initializing database state for: {db_url}")
            self.db_url = db_url
            self._connected = True
            self._initialized = True  # Set guard flag!
        else:
            print("[__init__]: Already initialized. Skipping state overwrite.")


# --- Verification in Action ---

# Call 1: First creation (allocates memory and initializes state)
conn1 = DatabaseConnection("postgresql://user:pass@localhost:5432/rag_db")
# Output:
# [__new__]: No instance found. Allocating memory via super().__new__(cls)...
# [__init__]: Initializing database state for: postgresql://user:pass@localhost:5432/rag_db

# Call 2: Attempting to create a second connection with different URL
conn2 = DatabaseConnection("postgresql://attacker:fake@otherhost:5432/hacked")
# Output:
# [__new__]: Existing instance found. Returning cached instance...
# [__init__]: Already initialized. Skipping state overwrite.

# Proof of Singleton identity:
print(conn1 is conn2)    # True! Both variables point to the EXACT same memory address
print(conn2.db_url)      # 'postgresql://user:pass@localhost:5432/rag_db' (safe from overwrite!)
```

###### The Signature Matching Rule Between `__new__` and `__init__`

When you instantiate a class by calling `MyClass(arg1, arg2, key=val)`, Python performs a coordinated dual-invocation:
1. First, it calls `MyClass.__new__(MyClass, arg1, arg2, key=val)`.
2. Second, if `__new__` returns an instance of `MyClass`, Python calls `instance.__init__(arg1, arg2, key=val)`.

> [!IMPORTANT]
> **The Signature Matching Rule:**  
> Because Python passes the **exact same arguments** to both `__new__` and `__init__`, their parameter signatures **must be compatible**:
> * If `__new__(cls, a)` only takes 1 argument, but `__init__(self, a, b)` expects 2 arguments:  
>   Calling `MyClass(1, 2)` crashes immediately in `__new__`:  
>   `TypeError: MyClass.__new__() takes 2 positional arguments but 3 were given`
> * If `__new__(cls, a, b)` takes 2 arguments, but `__init__(self, a)` expects 1:  
>   Calling `MyClass(1, 2)` crashes in `__init__`:  
>   `TypeError: MyClass.__init__() takes 2 positional arguments but 3 were given`
> 
> **The Architect's Practice:** When overriding `__new__`, either:
> 1. Mirror the exact same parameter list as `__init__`, OR
> 2. Use `def __new__(cls, *args, **kwargs):` to flexibly absorb all incoming arguments, delegating strict parameter validation to `__init__`.

> ⚠️ **The `object.__new__()` Single-Argument Trap:**  
> Python's root allocator `object.__new__(cls)` has a strict rule in Python 3: if `cls` overrides `__init__`, passing extra arguments to `super().__new__(cls, *args, **kwargs)` raises:  
> `TypeError: object.__new__() takes exactly one argument (the type to instantiate)`  
> **The Fix:** When delegating to Python's root allocator via `super().__new__(cls)`, pass **only `cls`**, never extra arguments! Let Python pass the arguments to `__init__` automatically.

###### Polymorphic Factory Pattern via `__new__` (Vehicle, Motorbike, Car)

A powerful capability of `__new__` is that it **can return an instance of a completely different class**! This enables the classic **Factory Pattern**: callers simply instantiate the base class `Vehicle(wheels=2, ...)` or `Vehicle(wheels=4, ...)`, and `__new__` transparently constructs and returns the specialized subclass:

```python
class Vehicle:
    def __new__(cls, wheels: int, brand: str):
        # 1. Intercept calls to the base class 'Vehicle(...)':
        if cls is Vehicle:
            if wheels == 2:
                print(f"[Vehicle.__new__]: 2 wheels detected -> instantiating Motorbike")
                # Delegates allocation of Motorbike to root allocator:
                return super().__new__(Motorbike)
            elif wheels == 4:
                print(f"[Vehicle.__new__]: 4 wheels detected -> instantiating Car")
                # Delegates allocation of Car to root allocator:
                return super().__new__(Car)
            else:
                raise ValueError(f"Cannot construct vehicle: unsupported wheel count ({wheels})")
        
        # 2. If a subclass was called directly (e.g. Car(4, "Tesla")), allocate normally:
        return super().__new__(cls)


class Motorbike(Vehicle):
    def __init__(self, wheels: int, brand: str):
        # Python automatically calls Motorbike.__init__ because
        # isinstance(instance, Vehicle) is True!
        self.wheels = wheels
        self.brand = brand

    def drive(self):
        return f"Riding a {self.wheels}-wheel {self.brand} motorbike!"


class Car(Vehicle):
    def __init__(self, wheels: int, brand: str):
        # Python automatically calls Car.__init__ with matching signature:
        self.wheels = wheels
        self.brand = brand

    def drive(self):
        return f"Driving a {self.wheels}-wheel {self.brand} car!"


# --- Verification in Action ---

# Call 1: Request 2 wheels -> Returns a Motorbike instance!
v1 = Vehicle(2, "Ducati")
print(f"Type: {type(v1).__name__} | Action: {v1.drive()}")
# Output:
# [Vehicle.__new__]: 2 wheels detected -> instantiating Motorbike
# Type: Motorbike | Action: Riding a 2-wheel Ducati motorbike!

# Call 2: Request 4 wheels -> Returns a Car instance!
v2 = Vehicle(4, "Porsche")
print(f"Type: {type(v2).__name__} | Action: {v2.drive()}")
# Output:
# [Vehicle.__new__]: 4 wheels detected -> instantiating Car
# Type: Car | Action: Driving a 4-wheel Porsche car!

# Call 3: Request invalid wheels -> Raises ValueError cleanly
try:
    v3 = Vehicle(18, "Freightliner")
except ValueError as e:
    print(f"Caught expected error: {e}")
# Output: Caught expected error: Cannot construct vehicle: unsupported wheel count (18)
```

###### Why Did `__init__` Run Automatically for `Motorbike` and `Car`?

Notice something subtle but critical: in the example above, we never explicitly called `Motorbike.__init__()` inside `Vehicle.__new__`. Yet `v1.brand` and `v1.wheels` were initialized perfectly! Why?

**Python's Internal Rule (Language Specification 3.3.1):**
* When you call `Vehicle(wheels, brand)`, Python captures the returned instance from `Vehicle.__new__`.
* Python checks: `isinstance(returned_instance, Vehicle)`?
* Because `Motorbike` and `Car` inherit from `Vehicle`, the check is **`True`**!
* Therefore, Python **automatically invokes `returned_instance.__init__(wheels, brand)`** on the resulting object!
* If `Motorbike` did *not* inherit from `Vehicle`, Python would skip `__init__` entirely, requiring you to initialize the instance manually before returning it.

> [!TIP]
> **Architect's Rule: What belongs in `__init__` (and what to avoid)**
> * ✅ **Belongs in `__init__`:** Validating arguments (raising `ValueError` for bad inputs), setting baseline attributes, and computing fast derived fields (e.g. `self.area = width * height`).
> * 🚫 **Avoid in `__init__`:** Slow or failure-prone side effects (e.g. downloading 5 GB model weights from Hugging Face, opening live database sockets, or calling external APIs). If an exception occurs inside `__init__`, the object fails to construct entirely. Keep heavy I/O in an explicit method (e.g. `await client.connect()`) or a `@classmethod` factory.

##### Code Contrast: The Heavy `__init__` Anti-Pattern vs. The AI-Engineer Pattern

```python
# 🚫 THE ANTI-PATTERN: Heavy, failure-prone operations inside __init__
class EmbeddingService:
    def __init__(self, model_url):
        self.model_url = model_url
        # 💥 PROBLEM: If network drops or times out, instantiation crashes!
        # You cannot instantiate this in a unit test without hitting real network.
        self.weights = requests.get(f"{model_url}/weights").content 


# ✅ THE CLEAN PATTERN: Keep __init__ lightweight; decouple heavy I/O
class EmbeddingService:
    def __init__(self, model_name, api_key):
        # 1. __init__ only validates and stores configuration (runs in < 1 millisecond):
        if not api_key:
            raise ValueError("API key required")
        self.model_name = model_name
        self.api_key = api_key
        self._connected = False

    # 2. Explicit lifecycle method for external network/socket setup:
    def connect(self):
        """Call explicitly when ready to perform the network connection."""
        print(f"Connecting to {self.model_name}...")
        self._connected = True

    # 3. OR use an alternative constructor factory (The HuggingFace pattern):
    @classmethod
    def from_pretrained(cls, path_or_url, api_key):
        """Standard AI pattern: factory method handles heavy loading, then returns instance."""
        service = cls("CustomModel", api_key)
        service.connect()
        return service
```

**Why this distinction matters in production:**
1. **Unit Testing:** You can test your service logic using mock data without making real network calls.
2. **Predictable Instantiation:** Creating an object is instantaneous and deterministic.
3. **Resilience & Reconnection:** If a connection drops, you can simply call `service.connect()` again without throwing away and reconstructing the entire object.





### 12.2 Instance vs class attributes (and the shared-state trap)

Attributes can belong either to the **class as a whole** (shared across all instances) or to a **specific instance**:

```python
class Dog:
    species = "Canis familiaris"     # CLASS attribute: shared by ALL instances
    def __init__(self, name):
        self.name = name             # INSTANCE attribute: unique to THIS instance

rex = Dog("Rex")
fido = Dog("Fido")

print(Dog.species)    # 'Canis familiaris' (accessed via the class)
print(rex.species)    # 'Canis familiaris' (accessed via instance — falls back to class)
print(rex.name)       # 'Rex' (unique to rex)
```

#### ⚠️ The Trap: Mutable class attributes act like shared static variables

If you define a **mutable** container (like a `list` or `dict`) at the class level, **all instances share the exact same container in memory**. Modifying it through one instance silently pollutes every other instance!

```python
# 🚫 THE BUG: Mutable class attribute acts as shared state across all objects
class Dog:
    tricks = []                      # CLASS attribute (mutable list) — SHARED by every dog!

    def __init__(self, name):
        self.name = name

    def add_trick(self, trick):
        self.tricks.append(trick)    # Appends to the ONE shared list in memory!

rex = Dog("Rex")
buddy = Dog("Buddy")

rex.add_trick("roll over")

# Look at buddy's tricks without ever teaching him a trick:
print(buddy.tricks)                  # ['roll over']  <- 💥 POLLUTED! Buddy shares rex's list!
print(rex.tricks is buddy.tricks)    # True — both point to the EXACT same list in memory!
```

#### ✅ The Fix: Initialize mutable data per instance inside `__init__`

Always put instance-specific state (lists, dicts, sets, objects) inside `__init__` attached to `self`:

```python
# ✅ THE FIX: Create a fresh list per instance inside __init__
class Dog:
    def __init__(self, name):
        self.name = name
        self.tricks = []             # INSTANCE attribute: a brand-new list for THIS dog

    def add_trick(self, trick):
        self.tricks.append(trick)    # Appends only to this specific dog's list

rex = Dog("Rex")
buddy = Dog("Buddy")

rex.add_trick("roll over")

print(rex.tricks)                    # ['roll over']
print(buddy.tricks)                  # []  <- Clean! Buddy's list is completely independent
print(rex.tricks is buddy.tricks)    # False — two separate list objects in memory
```

> **Rule of thumb:** Use class attributes only for constants, shared configurations, or class-level counters. Never put a mutable object (`[]`, `{}`) at the class level unless you deliberately want a shared global cache.

### 12.3 Inheritance — building on an existing class

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."

class Cat(Animal):                   # Cat INHERITS from Animal (gets its attributes/methods)
    def speak(self):                 # OVERRIDE: replace the parent's version
        return f"{self.name} says meow"

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)       # call the PARENT's __init__ to set up "name"
        self.breed = breed
    def speak(self):
        return f"{self.name} says woof"

# Polymorphism: same call, different behaviour depending on the actual type.
for animal in [Cat("Min"), Dog("Rex", "Lab")]:
    print(animal.speak())            # Min says meow / Rex says woof
```

**Polymorphism** means code can call `.speak()` on any `Animal` without knowing its exact subclass.

#### 🔍 Deep Dive: Method Overriding & The Role of `super()`

**Method Overriding** occurs when a subclass defines a method with the exact same name as a method in its parent class.

When overriding any method in Python, `super()` defines whether you are **replacing** or **extending** the parent's logic:

| Override Strategy | Do You Call `super()`? | What Happens? | When to Use It |
| :--- | :--- | :--- | :--- |
| **1. Pure Override (Replacement)** | 🚫 **No** | The parent's logic is completely bypassed and discarded. | When the child requires completely different logic (e.g., `Cat.speak()` returns `"meow"`, ignoring `Animal.speak()`). |
| **2. Augmented Override (Extension)** | ✅ **Yes (`super().method()`)** | The child invokes the parent's core engine, adding pre- or post-processing. | When you want to keep the parent's functionality while adding validation, logging, or state enrichment. |

##### 1. Why `super().__init__()` is Mandatory in Subclasses
In Python, **defining `__init__` in a subclass completely overrides the parent's `__init__`**. The parent initialization does **NOT** run automatically!

```python
# 🚫 THE BUG: Skipping super().__init__()
class Dog(Animal):
    def __init__(self, name, breed):
        # Forgot super().__init__(name)!
        self.breed = breed

d = Dog("Rex", "Lab")
print(d.name)  # 💥 AttributeError: 'Dog' object has no attribute 'name'!
```
Because `super().__init__(name)` was omitted, `self.name` was never created. Calling `d.speak()` will also crash. Always call `super().__init__(...)` to ensure parent state is properly configured.

##### 2. `super()` in Regular Methods: Extending vs. Replacing Behavior
You can use `super()` in any method, not just `__init__`. This allows a subclass to **extend** the parent's behavior by running the parent logic first, then adding custom steps:

```python
class BaseAgent:
    def execute(self, task):
        print(f"[Core Engine]: Executing {task}...")
        return {"status": "success"}

class GuardrailedAgent(BaseAgent):
    def execute(self, task):
        # 1. Pre-execution safety check:
        if "malicious" in task:
            raise ValueError("Task blocked by safety guardrail!")

        # 2. Call parent's execute() via super():
        result = super().execute(task)

        # 3. Post-execution enrichment:
        result["safety_checked"] = True
        return result

agent = GuardrailedAgent()
print(agent.execute("Analyze data"))
# Output:
# [Core Engine]: Executing Analyze data...
# {'status': 'success', 'safety_checked': True}
```

##### 3. Modern Python 3 vs. Legacy Python 2
* **Modern Python 3:** Simply write `super().method(...)` with zero arguments. Python automatically identifies the current class and instance.
* **Legacy Python 2 (awareness only):** Older codebases had to explicitly write `super(CurrentClass, self).method(...)`. Never use this in new Python code.

> 💡 **Is there an `override` keyword in Python?**  
> In Python, no keyword is required at runtime — simply defining a method with the same name in a subclass automatically overrides the parent.  
> *(Python 3.12+ note)*: Python 3.12 introduced the `@typing.override` decorator from the `typing` module purely as a static typing check to catch typos (e.g. if you accidentally typed `def speek(self):` instead of `def speak(self):`).



### 12.4 Dunder methods — make objects behave naturally

"Dunder" (Double UNDERscore) methods are special methods with leading and trailing double underscores that Python invokes automatically in response to specific language operations (such as `print()`, `==`, `+`, or `len()`).

#### 1. Object String Representation: `__str__` vs. `__repr__`

Python provides two separate methods for converting an object to a string. They serve different audiences and are triggered by different operations:

| Method | Intended Audience | Purpose | When Python Calls It Automatically |
| :--- | :--- | :--- | :--- |
| **`__str__`** | **End-User / Human** | Readable, friendly, informal display. | • `print(obj)`<br>• `str(obj)`<br>• `f"{obj}"` or `format(obj)` |
| **`__repr__`** | **Developer / Debugger** | Unambiguous, technical representation (ideally valid Python code to recreate the object). | • Typing `obj` in REPL / Jupyter notebook<br>• Debugger inspection<br>• `repr(obj)` or `f"{obj!r}"`<br>• **Inside containers:** `print([obj1, obj2])` or dict values |

##### Code Example & Automatic Triggers

```python
class ModelConfig:
    def __init__(self, name, temperature):
        self.name = name
        self.temperature = temperature

    # 1. __repr__: For developers (unambiguous, ideally reconstructs the object)
    def __repr__(self):
        return f"ModelConfig(name={self.name!r}, temperature={self.temperature})"

    # 2. __str__: For humans (pretty, clean display)
    def __str__(self):
        return f"Model '{self.name}' (Temp: {self.temperature})"


cfg1 = ModelConfig("gpt-4o", 0.7)
cfg2 = ModelConfig("claude-3-5-sonnet", 0.2)

# --- Automatic __str__ Triggers ---
print(cfg1)                      # Calls __str__  -> "Model 'gpt-4o' (Temp: 0.7)"
display_text = f"Using {cfg1}"   # Calls __str__  -> "Using Model 'gpt-4o' (Temp: 0.7)"
str_output = str(cfg1)           # Calls __str__

# --- Automatic __repr__ Triggers ---
cfg1                             # In REPL / Debugger -> ModelConfig(name='gpt-4o', temperature=0.7)
repr_output = repr(cfg1)         # Calls __repr__

# ⚠️ THE CONTAINER GOTCHA: Containers ALWAYS call __repr__ on their items!
configs = [cfg1, cfg2]
print(configs)
# Output: [ModelConfig(name='gpt-4o', temperature=0.7), ModelConfig(name='claude-3-5-sonnet', temperature=0.2)]
# Notice: Even though print() was called on the list, Python calls __repr__ for the items inside it!
```

##### The Fallback Mechanism & The Golden Rule

```
Caller requests string representation:
              │
              ▼
       Does __str__ exist?
          ├── YES ──> Call __str__()
          └── NO  ──> Does __repr__ exist?
                         ├── YES ──> Fall back to __repr__()  ✅
                         └── NO  ──> Default memory address: <ModelConfig object at 0x7f...>  🚫
```

> [!IMPORTANT]
> **The Golden Rule: Always implement `__repr__` first!**
> * If you define **only `__str__`**, viewing your object inside a list, dictionary, or debugger falls back to the ugly default memory address: `<ModelConfig object at 0x7f8...>`.
> * If you define **only `__repr__`**, Python **automatically falls back to `__repr__`** when someone calls `print(obj)` or `str(obj)`.
> * **Standard Practice:** Always write `__repr__` first. Add `__str__` only when you need a separate, polished display format for end-users.

#### 2. Equality (`__eq__`), `self.__dict__`, and Nested Property Equality

By default, custom Python objects do **not** compare their field values. If you do not implement `__eq__`, Python checks **identity** (`is` / memory address):

```python
class Item:
    def __init__(self, name): self.name = name

print(Item("Laptop") == Item("Laptop"))  # False! (Two different objects in memory)
```

##### (a) What is `self.__dict__`?
Every standard Python object stores its writable instance attributes in an internal dictionary accessible as **`self.__dict__`**:

```python
class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role

u = User("Alice", "Admin")
print(u.__dict__)  # {'name': 'Alice', 'role': 'Admin'}
```
When you assign `self.name = "Alice"`, Python literally inserts `'name': 'Alice'` into `self.__dict__`.

##### (b) Implementing `__eq__`: Field-by-Field vs. `__dict__`
When implementing `__eq__`, you can compare specific fields or compare the entire dictionary:

```python
class User:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def __eq__(self, other):
        # 1. Type guard: return NotImplemented so Python can ask the other operand
        if not isinstance(other, User):
            return NotImplemented

        # Approach A: Explicit attribute tuple check (fast, selective)
        return (self.name, self.role) == (other.name, other.role)

        # Approach B: Full dictionary equality check (compares all attributes automatically)
        # return self.__dict__ == other.__dict__
```

> **Why `return NotImplemented` instead of `False`?**  
> If `isinstance(other, User)` fails, returning `NotImplemented` tells Python: *"I don't know how to compare myself to this type — ask the `other` object if its `__eq__` method knows how to compare to me."* If neither knows, Python defaults to `False`.

##### (c) How Nested Property Equality Works (and The Hidden Trap)

What happens when an object contains **nested custom objects** (e.g. a `Customer` containing an `Address` instance)?

When evaluating `cust1 == cust2` (either via `self.address == other.address` or `self.__dict__ == other.__dict__`), Python recursively calls `==` on each attribute.

```python
class Address:
    def __init__(self, city, zip_code):
        self.city = city
        self.zip_code = zip_code

    # ✅ Must implement __eq__ on the nested child class too!
    def __eq__(self, other):
        if not isinstance(other, Address):
            return NotImplemented
        return self.__dict__ == other.__dict__


class Customer:
    def __init__(self, name, address):
        self.name = name
        self.address = address   # Nested custom object!

    def __eq__(self, other):
        if not isinstance(other, Customer):
            return NotImplemented
        # Comparing self.__dict__ automatically delegates equality down to self.address == other.address:
        return self.__dict__ == other.__dict__


addr1 = Address("Seattle", "98101")
addr2 = Address("Seattle", "98101")

c1 = Customer("Alice", addr1)
c2 = Customer("Alice", addr2)

print(c1 == c2)  # True! (Recursively compares name, then compares nested Address)
```

> ⚠️ **THE NESTED EQUALITY TRAP:**  
> If `Address` did **NOT** implement `__eq__`, comparing `c1 == c2` would compare `addr1 == addr2`, which would fall back to identity comparison (`addr1 is addr2`) and return **`False`**, even though both addresses have identical text!
> **Rule:** For nested equality to succeed with `==` or `__dict__ == other.__dict__`, **every nested custom class down the hierarchy must implement `__eq__`** (or be declared as a `@dataclass`, which generates recursive `__eq__` automatically).

#### 3. Operator Dunder Methods (`__add__`, etc.)

Dunders also allow custom objects to interact naturally with arithmetic operators:

```python
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        return f"Money({self.amount})"

    def __str__(self):
        return f"${self.amount:.2f}"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount

    def __add__(self, other):            # defines what "+" means
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        return Money(self.amount + other.amount)


m1 = Money(10)
m2 = Money(10)
m3 = Money(25)

print(m1 == m2)           # True  (thanks to __eq__)
print(str(m1 + m3))       # '$35.00' (thanks to __add__ creating Money(35), formatted by __str__)
```

### 12.5 Properties, alternative constructors (@classmethod), and static methods

#### 1. Constructor Overloading in Python: How to handle multiple initialization formats

In Python, **you cannot define multiple `__init__` methods with different parameter lists**. If you define two `def __init__` methods, the second one silently overwrites the first.

Instead, Python provides two clean, idiomatic solutions:

##### Solution A: Default and keyword arguments (for optional parameters)
When the initialization data differs only by which parameters are supplied, use default values:

```python
class Document:
    # Handles 1, 2, or 3 arguments cleanly in one __init__
    def __init__(self, text, metadata=None, author="Unknown"):
        self.text = text
        self.metadata = metadata if metadata is not None else {}
        self.author = author

doc1 = Document("Hello world")
doc2 = Document("Summary text", author="Alice")
doc3 = Document("AI Notes", {"tokens": 120}, "Bob")
```

##### Solution B: Alternative constructors with `@classmethod` (for different data representations)
When you need to construct an object from **different formats** (e.g. from a raw string, a JSON payload, or a dictionary), write a `@classmethod` that acts as a factory:

- A `@classmethod` receives the class itself as its first argument (named **`cls`** by convention, just like `self` for instances).
- It parses the input, transforms the data, and returns `cls(...)` — calling `__init__` with the parsed fields.

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    # Alternative constructor: builds a User from "Name, Age" string
    @classmethod
    def from_string(cls, text):
        name, age = text.split(",")
        return cls(name.strip(), int(age.strip()))  # calls User(name, age)

    # Alternative constructor: builds a User from a dictionary
    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["age"])

# Primary constructor:
u1 = User("Rex", 5)

# Alternative constructors (clean and readable!):
u2 = User.from_string("Alice, 30")
u3 = User.from_dict({"name": "Bob", "age": 25})

print(u2.name, u2.age)   # 'Alice' 30
print(u3.name, u3.age)   # 'Bob' 25
```

> **Why `cls(...)` instead of `User(...)`?**
> Using `cls` ensures that if another class inherits from `User`, calling `SubUser.from_string(...)` correctly returns an instance of `SubUser`, not the base `User`.

#### 2. Encapsulation: Private Attributes (`_variable`) & `@property` (Getter, Setter, Deleter)

In Python, there are **no `private` or `protected` keywords**. Instead, Python uses established naming conventions and the `@property` decorator suite to control how object attributes are accessed, updated, and removed.

##### (a) Access Levels: Public vs. Protected (`_`) vs. Private (`__`)

In Python, there are **no `public`, `protected`, or `private` keywords**. Visibility rules apply **identically to both variables and methods**:

| Access Level | Syntax Pattern | Meaning & Convention | Can It Be Accessed Outside the Class? |
| :--- | :--- | :--- | :--- |
| **Public** | `self.data`<br>`def action(self):` | Part of the public API. | ✅ Yes, completely open (`obj.data`, `obj.action()`). |
| **Protected** *(convention)* | `self._data`<br>`def _helper(self):` | Internal helper intended only for the class and its subclasses. | ⚠️ Yes (`obj._data`, `obj._helper()`), but doing so violates convention ("consenting adults" rule). |
| **Private** *(name mangling)* | `self.__data`<br>`def __secret(self):` | Name-mangled by Python to prevent subclass collisions. | 🚫 Direct `obj.__data` or `obj.__secret()` raises `AttributeError`.<br>🔓 Can still be accessed explicitly via `obj._ClassName__data` or `obj._ClassName__secret()`! |

##### Code Example: Private Variables and Private Methods in Action

```python
class BankVault:
    def __init__(self, pin):
        self.location = "New York"            # 1. Public variable
        self._security_level = 3              # 2. Protected variable (single _)
        self.__secret_pin = pin               # 3. Private variable (double __)

    # 4. Public Method: intended for callers
    def unlock(self, entered_pin):
        if self.__verify_pin(entered_pin):    # Calls private method internally!
            return "Vault unlocked! Welcome."
        return "Access denied: Invalid PIN."

    # 5. Protected Helper Method (convention only):
    def _audit_log(self, message):
        print(f"[AUDIT LOG - Level {self._security_level}]: {message}")

    # 6. Private Method (Name Mangled by Python):
    def __verify_pin(self, entered_pin):
        self._audit_log("Verifying PIN...")
        return entered_pin == self.__secret_pin


vault = BankVault("9876")

# --- (1) Public Interaction ---
print(vault.unlock("9876"))
# Output:
# [AUDIT LOG - Level 3]: Verifying PIN...
# Vault unlocked! Welcome.


# --- (2) Protected Method Access ---
vault._audit_log("Manual check")   # Works! But linters/conventions flag it as bad practice.


# --- (3) Direct Private Method Access Fails ---
try:
    vault.__verify_pin("9876")     # 💥 Fails!
except AttributeError as e:
    print(f"Direct call blocked: {e}")
    # Output: Direct call blocked: 'BankVault' object has no attribute '__verify_pin'


# --- (4) Why it failed: Python's Name Mangling on Methods ---
# Python automatically renames `def __method()` to `_ClassName__method`:
# Inspecting class attributes:
print([m for m in dir(vault) if "verify_pin" in m])
# Output: ['_BankVault__verify_pin']


# --- (5) How to EXPLICITLY call a Private Method (Bypassing Name Mangling) ---
# Format: obj._ClassName__methodName()
is_valid = vault._BankVault__verify_pin("9876")
print(f"Bypassed call result: {is_valid}")  # True!
```

> 💡 **Why does Method Name Mangling exist?**  
> Just like private variables, private methods are mangled to **prevent subclasses from accidentally overriding internal machinery**.
> If a parent class's `unlock()` relies on its own `__verify_pin()`, and a subclass author writes a new `def __verify_pin()` with different parameters or logic, Python ensures the parent's `_Parent__verify_pin` stays intact. The subclass cannot accidentally hijack the base class's internal method!
>
> **Standard Practice:** 
> - For internal helper methods you want to keep hidden from the public interface, use a single underscore `def _helper(self):`.
> - Use `def __private_method(self):` only when building deep inheritance frameworks where preventing subclass method overrides is critical.

##### (b) Inheritance: What Can Subclasses Actually Access? (`_` vs. `__`)

When a child class inherits from a parent, what members can the child method access directly?

| Member Type in Parent | Syntax | Accessible Directly in Child Class? | Why / How It Works |
| :--- | :--- | :--- | :--- |
| **Public** | `self.x`<br>`def f(self):` | ✅ **Yes** | Inherited directly; completely open to subclass. |
| **Protected** | `self._x`<br>`def _f(self):` | ✅ **Yes** | Single underscore is intended for the class **and all subclasses**. Works directly via `self._x` or `self._f()`. |
| **Private** | `self.__x`<br>`def __f(self):` | 🚫 **Direct access FAILS**<br>🔓 *Explicit access works* | Python mangles `__x` inside `Child` to `_Child__x`, but Parent stored it as `_Parent__x`.<br>To reach it, child must explicitly write `self._Parent__x`. |

##### Code Example: Subclass Access to Protected vs. Private

```python
class Parent:
    def __init__(self):
        self.public_data = "Public: open to anyone"
        self._protected_data = "Protected: meant for Parent & Child subclasses"
        self.__private_data = "Private: isolated to Parent class only"

    def _protected_method(self):
        return "Parent's protected algorithm"

    def __private_method(self):
        return "Parent's private internal engine"


class Child(Parent):
    def run_subclass_checks(self):
        # 1. Public: works seamlessly
        print(self.public_data)            # ✅ 'Public: open to anyone'

        # 2. Protected: works seamlessly inside subclass!
        print(self._protected_data)        # ✅ 'Protected: meant for Parent & Child subclasses'
        print(self._protected_method())    # ✅ "Parent's protected algorithm"

        # 3. Private: DIRECT access in subclass FAILS!
        try:
            print(self.__private_data)     # 💥 Raises AttributeError!
        except AttributeError as e:
            print(f"Direct private variable access failed: {e}")
            # Error: 'Child' object has no attribute '_Child__private_data'

        try:
            self.__private_method()        # 💥 Raises AttributeError!
        except AttributeError as e:
            print(f"Direct private method access failed: {e}")
            # Error: 'Child' object has no attribute '_Child__private_method'

        # 4. How the child CAN explicitly access parent private members:
        # Format: self._ParentClassName__memberName
        print(self._Parent__private_data)      # 🔓 'Private: isolated to Parent class only'
        print(self._Parent__private_method())  # 🔓 "Parent's private internal engine"


child_instance = Child()
child_instance.run_subclass_checks()
```

> 🎯 **The Architect's Mental Model for Subclasses:**
> * If you want subclasses to inherit, reuse, or override an internal detail: **use single underscore `_member`** (Protected).
> * If you want to lock an internal detail so child classes can NEVER accidentally see, touch, or override it: **use double underscore `__member`** (Private / mangled).

##### (c) Controlled Access with `@property`: Getter, Setter, and Deleter
Instead of writing verbose Java-style methods like `get_balance()` and `set_balance(amount)`, Python uses `@property` so callers can use clean, natural attribute dot-notation (`account.balance = 100`) while your class executes validation logic under the hood:


- **Getter (`@property`)**: Runs automatically when reading `account.balance`. Returns the internal private `self._balance`.
- **Setter (`@<property_name>.setter`)**: Runs automatically when assigning `account.balance = 250`. Validates data and guards invariants before mutating `self._balance`.
- **Deleter (`@<property_name>.deleter`)**: Runs automatically when deleting `del account.balance`. Executes cleanup logic before clearing state.

```python
class BankAccount:
    def __init__(self, owner, initial_balance=0):
        self.owner = owner
        # Internal backing variable prefixed with _ (private convention):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._balance = initial_balance

    # 1. GETTER: accessed as `account.balance` (looks like an attribute, runs as a method)
    @property
    def balance(self):
        """Public getter: returns the private backing value."""
        return self._balance

    # 2. SETTER: accessed as `account.balance = 250`
    @balance.setter
    def balance(self, new_balance):
        """Public setter: validates before mutating the private backing value."""
        if not isinstance(new_balance, (int, float)):
            raise TypeError("Balance must be a number")
        if new_balance < 0:
            raise ValueError("Balance cannot be negative! Overdraft not permitted.")
        self._balance = new_balance    # ✅ Sets the private backing variable

    # 3. DELETER: accessed as `del account.balance`
    @balance.deleter
    def balance(self):
        """Public deleter: executes cleanup when the attribute is deleted."""
        print(f"Closing account and clearing balance for {self.owner}...")
        del self._balance


# --- Using the Managed Attribute ---
acc = BankAccount("Alice", 100)

# (1) GETTER in action:
print(acc.balance)           # 100 (clean dot-notation, no parentheses!)

# (2) SETTER in action:
acc.balance = 250            # Triggers @balance.setter
print(acc.balance)           # 250

# Validation guards in action:
try:
    acc.balance = -50        # Triggers ValueError in the setter!
except ValueError as e:
    print(f"Blocked: {e}")   # 'Blocked: Balance cannot be negative! Overdraft not permitted.'

# (3) DELETER in action:
del acc.balance              # Triggers @balance.deleter: prints closing message
```

> ⚠️ **CRITICAL GOTCHA: The Setter Infinite Recursion Loop**
> Inside `@balance.setter`, you **MUST** assign to the private backing variable `self._balance = new_balance`.
> If you accidentally write `self.balance = new_balance` (without the underscore), you are invoking the setter method inside itself, creating an infinite recursive loop that crashes with:
> `RecursionError: maximum recursion depth exceeded`!

##### (c) Read-Only Computed Properties
If you provide `@property` (getter) **without** defining a `.setter`, the attribute becomes **read-only**. Trying to assign to it raises an `AttributeError`:

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property                      # Read-only getter: no setter defined!
    def area(self):
        return 3.14159 * self.radius ** 2

c = Circle(2)
print(c.area)                      # 12.566... (computed on the fly)

# c.area = 50                      # 💥 AttributeError: property 'area' of 'Circle' object has no setter!
```

#### 3. Method Types Compared: Instance (`self`) vs. Class (`@classmethod`) vs. Static (`@staticmethod`)

Python classes support three distinct types of methods. Understanding their differences in arguments, access, initialization, and memory behavior is essential for clean architecture:

| Feature | Instance Method | Class Method (`@classmethod`) | Static Method (`@staticmethod`) |
| :--- | :--- | :--- | :--- |
| **First Argument** | **`self`** (the current instance) | **`cls`** (the class itself) | **None** (plain arguments only) |
| **Can Access Instance State (`self.x`)?** | ✅ **Yes** | 🚫 No | 🚫 No |
| **Can Access Class State (`cls.x`)?** | ✅ Yes (via `self.__class__.x`) | ✅ **Yes (directly via `cls.x`)** | ⚠️ Only by hardcoding `ClassName.x` |
| **Subclass Polymorphism?** | ✅ Yes | ✅ **Yes** (`cls` dynamically resolves to the child subclass) | 🚫 No (hardcoded class name won't adapt to subclasses) |
| **Can Call Without an Instance?** | 🚫 No (requires `obj.method()`) | ✅ **Yes** (`ClassName.method()`) | ✅ **Yes** (`ClassName.method()`) |
| **Primary Use Case** | Modifying or reading per-instance data. | Alternative constructors / factory methods, modifying class variables. | Isolated utility functions namespaced inside the class for logical grouping. |

##### Code Example: All Three in One Class

```python
class TextProcessor:
    # Class-level variable (shared configuration):
    default_encoding = "utf-8"

    def __init__(self, encoding=None):
        # Instance attribute:
        self.encoding = encoding or self.default_encoding

    # 1. INSTANCE METHOD: operates on a specific object's state (self)
    def process(self, text):
        cleaned = self.clean_whitespace(text)  # Can call static utility
        return cleaned.encode(self.encoding)    # Uses self.encoding

    # 2. CLASS METHOD (@classmethod): receives `cls`
    # Perfect for alternative constructors and class-variable inspection:
    @classmethod
    def from_ascii(cls):
        """Alternative constructor: returns a TextProcessor configured for ASCII."""
        instance = cls(encoding="ascii")       # Uses cls() so subclasses inherit properly!
        return instance

    @classmethod
    def set_default_encoding(cls, new_encoding):
        """Modifies class-level state dynamically."""
        cls.default_encoding = new_encoding

    # 3. STATIC METHOD (@staticmethod): receives neither self nor cls
    # Pure function that does not depend on instance or class state:
    @staticmethod
    def clean_whitespace(text):
        return " ".join(text.strip().split())


# --- Execution & Verification ---

# Using @staticmethod (callable on class or instance, no state needed):
clean = TextProcessor.clean_whitespace("  hello    world \n ")
print(clean)                             # 'hello world'

# Using @classmethod (alternative constructor without creating base instance first):
ascii_proc = TextProcessor.from_ascii()
print(ascii_proc.encoding)               # 'ascii'

# Using Instance Method (requires an initialized object):
proc = TextProcessor()
print(proc.process(" AI engineering "))  # b'AI engineering'
```

##### Deep Dive: Key Technical Nuances

1. **Can a `@staticmethod` use class variables?**
   - **Yes, but with a major catch:** Because `@staticmethod` receives neither `self` nor `cls`, it cannot dynamically discover its class. To read a class variable, it must **hardcode** the class name: `TextProcessor.default_encoding`.
   - **Why `@classmethod` is superior for class variables:** If a subclass `CustomProcessor(TextProcessor)` overrides `default_encoding = "utf-16"`, a `@classmethod` automatically sees `"utf-16"` via `cls.default_encoding`. A `@staticmethod` with hardcoded `TextProcessor.default_encoding` would still see `"utf-8"`, breaking polymorphism!

2. **Initialization & Lifecycle:**
   - **When are they initialized?** Both `@classmethod` and `@staticmethod` are created and bound when the Python interpreter parses the class definition (at module import time). 
   - They exist in memory regardless of whether zero, one, or ten thousand instances of the class are created.

3. **Memory & Garbage Collection (GC) Impact:**
   - **Instance Methods:** Accessing `obj.method` creates a temporary **bound method object** dynamically in memory (which binds the function to the `obj` reference).
   - **Static Methods:** Calling `ClassName.static_method` or `obj.static_method` returns the **raw, underlying function object directly** from the class dictionary (`TextProcessor.__dict__['clean_whitespace'].__func__`). No bound wrapper object is created, making it slightly more lightweight.
   - **Garbage Collection Safety:** Neither `@staticmethod` nor `@classmethod` holds a reference to instance objects (`self`). Therefore, they **never prevent instances from being garbage collected** and cannot cause instance circular-reference memory leaks.

4. **Architect's Decision: `@staticmethod` vs. Module-Level Function?**
   - In Python, if a helper function does not touch `self` or `cls`, you have two choices:
     1. A `@staticmethod` inside the class.
     2. A standalone function at module level (`def clean_whitespace(text):` at the top of the file).
   - **Rule of thumb:** If the utility is closely tied to the conceptual domain of the class (or callers naturally expect `TextProcessor.clean_whitespace(...)`), keep it as `@staticmethod`. If it's a generic utility used by multiple different classes, move it to a module-level helper.


### 12.6 Dataclasses — classes for data, with less boilerplate

```python
from dataclasses import dataclass

@dataclass                         # auto-writes __init__, __repr__, __eq__ for you
class Point:
    x: int
    y: int

p = Point(1, 2)
print(p)                           # Point(x=1, y=2)  — readable repr for free
print(p == Point(1, 2))            # True
```

(When you also need **validation**, reach for a Pydantic model instead — that's Lesson 13.)

### 12.7 Enumerations (`Enum`): Typesafe Named Constants

When a variable can only take one of a fixed set of options (e.g. LLM roles, task statuses, model tiers), using raw strings (`"admin"`, `"user"`) is fragile because typos (`"admim"`) fail silently at runtime. Python provides the **`enum`** module to define type-safe enumerations.

#### 1. Defining an Enum & Accessing `.name` and `.value`
Every member of an `Enum` is a constant object that possesses two primary attributes:
* **`.name`**: The member's variable name as a string (e.g., `"ADMIN"`).
* **`.value`**: The underlying value assigned to that member (e.g., `"admin"`, `1`, etc.).

```python
from enum import Enum, auto

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

current_role = Role.ADMIN

print(current_role)             # Role.ADMIN (the enum member object)
print(current_role.name)        # 'ADMIN' (member identifier as a string)
print(current_role.value)       # 'admin' (underlying value)
```

#### 2. What Types Can an Enum Value Be? (Int, String, Auto, or Custom)
An Enum value can be **any Python data type**:

```python
from enum import Enum, IntEnum, StrEnum, auto

# (a) Standard Enum with integer values:
class HTTPStatusCode(Enum):
    OK = 200
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

# (b) IntEnum (Subclasses int — directly comparable with integers):
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print(Priority.HIGH == 3)            # True! (IntEnum compares equal to raw ints)
print(Priority.HIGH > Priority.LOW)  # True! (supports ordering comparisons)

# (c) StrEnum (Python 3.11+ / Subclasses str — ideal for JSON & LLM APIs):
class ModelTier(StrEnum):
    FLAGSHIP = "gpt-4o"
    FAST = "gpt-4o-mini"
    EMBEDDING = "text-embedding-3-small"

print(ModelTier.FLAGSHIP == "gpt-4o")  # True! (StrEnum compares equal to raw strings)

# (d) auto() — Automatic value assignment (no manual numbering needed):
class AgentState(Enum):
    IDLE = auto()                    # gets 1
    PLANNING = auto()                # gets 2
    EXECUTING = auto()               # gets 3
    COMPLETED = auto()               # gets 4

# (e) Custom / Complex values (tuples, dicts):
class ModelSpec(Enum):
    # Tuple: (context_window, cost_per_1k_tokens)
    GPT4O = (128_000, 0.005)
    CLAUDE_SONNET = (200_000, 0.003)

print(ModelSpec.GPT4O.value[0])      # 128000
```

#### 3. How to Compare Enums
In Python, Enum members are **canonical singletons** (there is only ever one instance of `Role.ADMIN` in memory).

##### (a) Identity Comparison (`is` / `is not`) — THE RECOMMENDED WAY:
```python
user_role = Role.ADMIN

# ✅ FASTEST & SAFEST (checks memory identity directly):
if user_role is Role.ADMIN:
    print("Full administrative access granted.")

if user_role is not Role.GUEST:
    print("User is not a guest.")
```

##### (b) Equality Comparison (`==` / `!=`):
```python
if user_role == Role.ADMIN:
    print("Matches!")
```

> ⚠️ **The Standard `Enum` vs. Raw Value Trap:**
> In a standard `Enum`, members do **NOT** compare equal to their raw values!
> ```python
> class Status(Enum):
>     READY = 1
> 
> # ❌ TRAP:
> print(Status.READY == 1)        # False! Status.READY is an Enum object, not an int!
> print(Status.READY.value == 1)  # True (comparing the .value attribute)
> 
> # If you want direct equality with raw values, use IntEnum or StrEnum:
> class SafeStatus(IntEnum):
>     READY = 1
> 
> print(SafeStatus.READY == 1)    # True!
> ```

##### (c) Ordering Comparisons (`<`, `>`, `<=`, `>=`):
* Standard `Enum` members **do not have ordering**:
  `Role.ADMIN < Role.USER` raises `TypeError: '<' not supported between instances of 'Role' and 'Role'`.
* Use **`IntEnum`** when you need ordering comparisons (e.g., `Priority.HIGH > Priority.LOW`).

##### (d) Pattern Matching with `match / case`:
```python
state = AgentState.PLANNING

match state:
    case AgentState.IDLE:
        print("Waiting for prompt...")
    case AgentState.PLANNING:
        print("Generating execution plan...")
    case AgentState.EXECUTING:
        print("Running agent tools...")
    case _:
        print("Unknown state")
```

#### 4. Lookup by Value and Lookup by Name
Enums make it clean to parse incoming API strings into typed Enum instances:

```python
# 1. Lookup by Value: Enum(value)
# Useful when receiving raw strings from an external REST API or JSON payload:
incoming_data = "user"
role = Role(incoming_data)           # Returns Role.USER
print(role is Role.USER)             # True

# Invalid value raises ValueError:
# Role("superadmin")                 # 💥 ValueError: 'superadmin' is not a valid Role

# 2. Lookup by Name: Enum[name]
# Useful when looking up by the uppercase identifier string:
role = Role["ADMIN"]                 # Returns Role.ADMIN
```

#### 5. Iterating over Enum Members
```python
for member in Role:
    print(f"Name: {member.name:10} | Value: {member.value}")
# Output:
# Name: ADMIN      | Value: admin
# Name: USER       | Value: user
# Name: GUEST      | Value: guest
```

### 12.8 Abstract Base Classes (`ABC` & `@abstractmethod`)

In large AI architectures, you often need to define a strict **contract / interface** that multiple concrete components must follow (e.g. swapping between different LLM providers, vector stores, or embedding engines). Python provides the **`abc`** (Abstract Base Classes) module for this.

#### 1. Defining an Abstract Base Class (`ABC`)

To create an abstract contract in Python:
1. Inherit from **`ABC`** (`from abc import ABC, abstractmethod`).
2. Decorate every method that child classes *must* implement with **`@abstractmethod`**.

```python
from abc import ABC, abstractmethod

class BaseLLM(ABC):
    def __init__(self, model_name: str):
        self.model_name = model_name

    # Contract 1: Using '...' (Ellipsis) — Modern Python / Type-Stub convention
    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...

    # Contract 2: Using 'pass' — Traditional Python convention
    @abstractmethod
    def stream(self, prompt: str) -> str:
        pass

    # Concrete helper: subclasses inherit this as-is
    def format_system_prompt(self, user_text: str) -> str:
        return f"System: AI Assistant\nUser: {user_text}"
```

> [!NOTE]
> **Can an `@abstractmethod` use `...` (Ellipsis) instead of `pass`?**
> **Yes, absolutely!** In Python, `...` evaluates to the built-in `Ellipsis` singleton, making it a completely valid statement for a function body.
> * **`...` (Modern / PEP 484 convention):** Widely favored in modern Python, `.pyi` type stubs, and AI libraries because it explicitly conveys: *"This is a pure signature specification; implementation intentionally omitted."*
> * **`pass` (Traditional convention):** The classic Python way. Functionally identical to `...` at runtime.
> Both work identically because Python blocks instantiation at runtime if the method is not overridden.


#### 2. Instantiation Enforcement: What Happens When Violated?

Python strictly enforces abstract contracts **at instantiation time**:

```python
# 🚫 ATTEMPT 1: Instantiating the abstract class directly
try:
    llm = BaseLLM("generic")
except TypeError as e:
    print(f"Blocked: {e}")
    # Output: Blocked: Can't instantiate abstract class BaseLLM without an implementation for abstract method 'generate'


# 🚫 ATTEMPT 2: Subclass forgot to implement the abstract method
class MockLLM(BaseLLM):
    pass  # Forgot def generate()!

try:
    mock = MockLLM("mock-v1")
except TypeError as e:
    print(f"Subclass blocked: {e}")
    # Output: Subclass blocked: Can't instantiate abstract class MockLLM without an implementation for abstract method 'generate'


# ✅ ATTEMPT 3: Complete implementation
class OpenAIProvider(BaseLLM):
    def generate(self, prompt: str) -> str:
        return f"OpenAI ({self.model_name}) response to: {prompt}"

client = OpenAIProvider("gpt-4o")
print(client.generate("Hello"))  # Works! "OpenAI (gpt-4o) response to: Hello"
```

#### 3. Abstract Properties (`@property` + `@abstractmethod`)

You can force subclasses to provide a specific **attribute / property** by combining `@property` and `@abstractmethod`:

```python
class BaseEmbeddingModel(ABC):
    # Contract: Every subclass must provide an embedding_dim property
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        ...  # '...' (Ellipsis) or 'pass'


class MiniLM(BaseEmbeddingModel):
    @property
    def embedding_dim(self) -> int:
        return 384


model = MiniLM()
print(model.embedding_dim)  # 384
```

> ⚠️ **CRITICAL GOTCHA: Decorator Stacking Order (The "Innermost" Rule)**
> When combining `@abstractmethod` with other decorators (like `@property` or `@classmethod`), **`@abstractmethod` MUST ALWAYS BE THE INNERMOST (LAST / BOTTOM) DECORATOR**:
>
> ```python
> # ✅ CORRECT: @abstractmethod is innermost (closest to def)
> @property
> @abstractmethod
> def api_key(self):
>     pass
> 
> @classmethod
> @abstractmethod
> def from_config(cls, cfg):
>     pass
> 
> # 🚫 WRONG: Stacking in reverse order breaks descriptor machinery!
> @abstractmethod
> @property
> def api_key(self):
>     pass
> ```
> **Why?** Python evaluates decorators from the inside out (bottom to top). `@property` and `@classmethod` expect to wrap a callable that has already been flagged as abstract. Reversing the order breaks Python's descriptor machinery and causes subtle bugs or type-checker failures.

#### 4. Can an `@abstractmethod` Have Implementation Code?
**Yes!** An abstract method can provide default or shared baseline code in the base class. Subclasses must still override it, but they can invoke `super().method()` to reuse the base logic:

```python
class BaseAgent(ABC):
    @abstractmethod
    def run(self, task):
        # Baseline shared logging
        print(f"[BASE AGENT]: Task started -> {task}")

class CodeAgent(BaseAgent):
    def run(self, task):
        super().run(task)  # Executes base class abstract implementation!
        print("[CODE AGENT]: Generating Python solution...")

agent = CodeAgent()
agent.run("Refactor DB")
# Output:
# [BASE AGENT]: Task started -> Refactor DB
# [CODE AGENT]: Generating Python solution...
```

### 12.9 Protocols (`typing.Protocol`): Structural Subtyping & Static Duck Typing

Python has always been famous for **"duck typing"**:
> *"If it walks like a duck and quacks like a duck, it's a duck."*

In traditional dynamic Python, you don't check types upfront—you simply call `obj.quack()` and hope the object implements it. If it doesn't, Python crashes at runtime with an `AttributeError`.

Abstract Base Classes (`ABC`) solved this with **nominal subtyping** (explicit inheritance: `class Duck(Animal)`), but `ABC` forces classes to tightly couple to the base class by inheriting from it.

Introduced in Python 3.8 (PEP 544), **`Protocol`** gives Python **structural subtyping** (often called *static duck typing*): you define an interface contract, and **any class that has the matching methods/attributes automatically satisfies the protocol—without needing to inherit from it!**

#### 1. Defining a Protocol: Syntax & The Ellipsis (`...`)

To define a protocol:
1. Subclass `typing.Protocol`.
2. Write method signatures using **`...`** (the built-in `Ellipsis` singleton) as the method body.

```python
from typing import Protocol

class TextEmbedder(Protocol):
    # Pure method signature contract:
    def embed(self, text: str) -> list[float]:
        ...
```

> [!NOTE]
> **Why `...` (Ellipsis) instead of `pass`?**
> In Python syntax, both `pass` and `...` (an Ellipsis literal) are valid no-op statements. However, in Python typing conventions (PEP 484 and PEP 544):
> * **`pass`** generally means *"this block has nothing to execute right now"*.
> * **`...` (Ellipsis)** explicitly signals to developers, IDEs, and static type-checkers: *"This is a pure type signature / interface declaration whose implementation is deliberately omitted"*.
> 
> Using `...` is the universal, non-negotiable community standard for `Protocol` methods and `.pyi` type stub files.

#### 2. Structural Subtyping in Action: Zero-Coupling Interfaces

Notice that the following classes **do NOT inherit from `TextEmbedder`**. They don't even import `TextEmbedder`:

```python
# Provider A: In-memory mock
class FastMockEmbedder:
    def embed(self, text: str) -> list[float]:
        # Simple dummy vector of length 3
        return [0.1, 0.2, 0.3]

# Provider B: Third-party library wrapper
class HuggingFaceEmbedder:
    def __init__(self, model_tag: str):
        self.model_tag = model_tag

    def embed(self, text: str) -> list[float]:
        # Simulating external Hugging Face inference call
        return [0.45, -0.12, 0.88]

# Consumer function: expects anything that conforms to TextEmbedder
def index_document(content: str, embedder: TextEmbedder) -> list[float]:
    print("Indexing content with embedder...")
    vector = embedder.embed(content)
    return vector

# Both work seamlessly with type checkers and runtime execution!
mock_vec = index_document("Hello world", FastMockEmbedder())
hf_vec = index_document("Hello world", HuggingFaceEmbedder("all-MiniLM-L6-v2"))
```

If a class provides an incompatible `embed` signature (or omits it entirely), static type-checkers (like `mypy` or Pyright) will flag it with an error before you even run your code.

#### 3. Defining Attributes and Properties in Protocols

Protocols can enforce instance variables and properties in addition to methods:

```python
from typing import Protocol
from dataclasses import dataclass

class VectorDocument(Protocol):
    # Required attributes (with type annotations):
    page_content: str
    metadata: dict[str, str]

    # Required property:
    @property
    def token_count(self) -> int:
        ...

# Any dataclass or class with these attributes conforms automatically:
@dataclass
class KnowledgeChunk:
    page_content: str
    metadata: dict[str, str]

    @property
    def token_count(self) -> int:
        return len(self.page_content.split())

# KnowledgeChunk perfectly satisfies VectorDocument without subclassing it!
```

#### 4. Runtime Checking with `@runtime_checkable`

By default, `Protocol` is purely a **static analysis tool** for IDEs and type-checkers. If you try calling `isinstance(obj, TextEmbedder)` at runtime, Python raises:
`TypeError: Instance and class checks can only be used with @runtime_checkable protocols`

To allow runtime `isinstance()` and `issubclass()` checks, decorate the protocol with `@runtime_checkable`:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Searchable(Protocol):
    def search(self, query: str) -> list[str]:
        ...

class MemoryStore:
    def search(self, query: str) -> list[str]:
        return ["result1", "result2"]

class UnrelatedStore:
    def query(self, text: str) -> list[str]:
        return []

store1 = MemoryStore()
store2 = UnrelatedStore()

print(isinstance(store1, Searchable))  # True (it has a .search method)
print(isinstance(store2, Searchable))  # False (it lacks .search)
```

> ⚠️ **CRITICAL GOTCHA: `@runtime_checkable` Only Checks Name Existence!**
> At runtime, `@runtime_checkable` inspects whether an attribute or method **name exists** (`hasattr(obj, 'search')`).
> It does **NOT** validate parameter count, parameter types, or return types at runtime!
> ```python
> class BrokenStore:
>     search = "not even a method!"  # string, not a method
> 
> print(isinstance(BrokenStore(), Searchable))  # Still returns True!
> ```
> For full type validation, rely on static type checkers (`mypy` / `pyright`) or Pydantic validation (covered in Lesson 13).

---

#### 5. The Architect's Guide: `Protocol` vs. `ABC` (`@abstractmethod`)

When designing AI frameworks, pipelines, or toolsets, should you use `Protocol` or `ABC`?

| Dimension | `typing.Protocol` (Structural) | `abc.ABC` + `@abstractmethod` (Nominal) |
| :--- | :--- | :--- |
| **Subtyping Philosophy** | **Structural** ("Shape / Duck typing") | **Nominal** ("Name / lineage matching") |
| **Inheritance Required?** | ❌ **No**. Any class matching the signature conforms. | ✅ **Yes**. Subclasses must write `class MyClass(BaseABC):`. |
| **Coupling** | **Zero coupling**. Implementers don't even import the protocol. | **Tight coupling**. Implementers must import and inherit the base class. |
| **Third-Party Friendly** | ✅ **Flawless**. Third-party objects conform without modification. | ❌ **Rigid**. Requires writing wrapper or adapter classes. |
| **Enforcement Time** | **Static analysis** (`mypy`, IDEs). | **Runtime instantiation** (`TypeError` if instantiated without overrides). |
| **Code Reuse / Base Logic** | ❌ None (pure interface signatures). | ✅ **Rich**. Can provide base `__init__`, shared helper methods, and `super()` calls. |
| **Method Body Idiom** | `...` (Ellipsis) | `pass` or shared baseline implementation |

##### Decision Tree: When to Use What?

```
Do you need shared base implementation or state (__init__, helpers, super())?
├── YES ──> Use ABC (with inheritance & super())
└── NO  ──> Do you need third-party or arbitrary classes to satisfy the contract without modifying their source code?
            ├── YES ──> Use Protocol (Structural Subtyping)
            └── NO  ──> Do you want strict runtime instantiation crashes if a method is missing?
                        ├── YES ──> Use ABC
                        └── NO  ──> Use Protocol (cleaner, zero-coupling)
```

**Practical AI Engineering Rule of Thumb:**
* Use **`Protocol`** when defining what your functions **consume** (e.g. `def process(retriever: VectorRetriever)`), allowing callers to pass any client from third-party libraries (Hugging Face, LangChain, LlamaIndex, Chroma) without forcing them to inherit from your base class.
* Use **`ABC`** when creating an **extensible internal framework** where child components are expected to inherit boilerplate state, configuration management, lifecycle management, and logging hooks.

## 🚀 Stage 3 — In Practice / Why It Matters

Every library hands you objects: `client = OpenAI()` then `client.chat.completions.create(...)`.
Pydantic models, LangGraph state, embedding models — all classes. Knowing `__init__`, `self`,
methods, inheritance, and dunder methods means you can read library docs and source confidently.

**Common beginner mistakes (the reasoning):**
1. **Forgetting `self`** — methods must take `self` as the first parameter, and you use `self.x`
   to reach instance data. Omitting it causes confusing errors.
2. **Mutable class attributes** — a list defined at class level is shared by all instances (same
   trap as mutable default arguments). Put per-instance data in `__init__` via `self`.
3. **Confusing `__str__` and `__repr__`** — `__str__` is the friendly print; `__repr__` is the
   unambiguous debug form. Define `__repr__` at least.
4. **Overusing inheritance** — deep class trees get tangled; often a simple function or dataclass
   is enough.

### Try it yourself
Make a `BankAccount` class with `__init__(self, balance=0)`, a `deposit(amount)` method, and a
`@property` `is_overdrawn` that returns `True` when the balance is negative.

## 🐛 Common Errors & Fixes

| What you see | Cause | Fix |
| --- | --- | --- |
| `TypeError: method() missing 1 required positional argument: 'self'` | Forgot `self` in a method definition | Make `self` the first parameter |
| `TypeError: __init__() should return None, not '...'` | Explicitly returned a value from `__init__` | Remove the `return` statement; `__init__` must always return `None` |
| `AttributeError: object has no attribute 'x'` | Used `self.x` before it was set | Set it in `__init__` |
| `RecursionError: maximum recursion depth exceeded` | Assigned to `self.x = val` inside `@x.setter` instead of `self._x` | Assign to the private backing variable `self._x` inside the setter |
| `AttributeError: property 'x' of '...' object has no setter` | Assigned to a read-only property | Define an `@x.setter` method if mutation should be permitted |
| Multiple `def __init__` methods defined | The second definition silently overrides the first | Use default arguments or `@classmethod` alternative constructors |
| All instances share one list / dict | A mutable **class** attribute acted as shared state | Put per-instance collections inside `__init__` via `self` |
| `Status.READY == 1` returns `False` | Comparing standard `Enum` member directly to a raw integer | Compare against member (`status is Status.READY`), use `.value`, or use `IntEnum` |
| `TypeError: '<' not supported between instances of 'Role'` | Tried to sort or order standard `Enum` members | Standard `Enum` has no ordering; use `IntEnum` for ordered numeric enums |
| `ValueError: 'X' is not a valid Enum` | Called `Enum(value)` with an unregistered value | Verify input or handle invalid values with a `try/except ValueError` block |
| `AttributeError: 'X' object has no attribute '__y'` | Attempted direct access to private mangled attribute | Use public methods or access via `_ClassName__y` (debugging only) |
| Two identical objects return `False` with `==` | Class omitted `__eq__`, falling back to identity comparison (`is`) | Implement `def __eq__(self, other)` or use `@dataclass` |
| Nested custom objects return `False` with `==` | A nested child class omitted `__eq__` | Ensure all nested custom classes implement `__eq__` |
| `TypeError: Can't instantiate abstract class ...` | Subclass forgot to implement an `@abstractmethod` | Implement all abstract methods/properties in the child class |
| Unexpected behavior with `@abstractmethod` + `@property` | Decorators stacked in reverse order | Place `@abstractmethod` as the innermost (bottom) decorator |
| `TypeError: Instance and class checks can only be used with @runtime_checkable protocols` | Used `isinstance()` on a standard Protocol | Decorate the Protocol with `@runtime_checkable` |
| `isinstance(obj, Protocol)` returns `True` despite invalid types | `@runtime_checkable` only checks attribute name existence (`hasattr`) | Use static type checker (`mypy`) or Pydantic for deep signature validation |
| Singleton state overwritten on subsequent calls | Python calls `__init__` every time `Class()` is invoked, even when `__new__` returns cached instance | Guard `__init__` with `if not hasattr(self, "_initialized")` |
| `TypeError: object.__new__() takes exactly one argument` | Passed extra arguments to `super().__new__(cls, ...)` when `__init__` is overridden | Pass only `cls` to `super().__new__(cls)` |
| `TypeError: __new__() takes X positional arguments but Y were given` | Mismatched parameter signatures between `__new__` and `__init__` | Ensure `__new__` and `__init__` accept matching arguments, or use `*args, **kwargs` in `__new__` |
| Parent setup didn't happen | Subclass `__init__` skipped the parent | Call `super().__init__(...)` |

## 📌 Quick Reference

```python
class Dog(Animal):
    species = "canine"             # class attribute (shared immutable constant)
    def __init__(self, name):
        super().__init__(name)     # parent setup
        self.name = name           # instance attribute
        self.tricks = []           # per-instance collection (not shared!)

    def speak(self): return "woof"
    def __repr__(self): return f"Dog({self.name})"

    # Alternative constructor:
    @classmethod
    def from_string(cls, s):
        return cls(s.strip())

class Account:
    def __init__(self, balance):
        self._balance = balance    # private by convention

    @property
    def balance(self):             # GETTER: acc.balance
        return self._balance

    @balance.setter
    def balance(self, val):        # SETTER: acc.balance = val
        if val < 0: raise ValueError("Negative!")
        self._balance = val        # assign to private backing variable!

    @balance.deleter
    def balance(self):             # DELETER: del acc.balance
        del self._balance

# Singleton using __new__:
class SingletonConnection:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # delegates to object.__new__(cls)
        return cls._instance


from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int

from enum import Enum, IntEnum, StrEnum, auto
class Role(StrEnum):
    ADMIN = "admin"
    USER = "user"

role is Role.ADMIN                  # identity comparison (fastest & safest)
role.name                           # 'ADMIN' (identifier string)
role.value                          # 'admin' (underlying value)
Role("admin")                       # lookup by value -> Role.ADMIN
Role["ADMIN"]                       # lookup by name  -> Role.ADMIN

from abc import ABC, abstractmethod
class BaseService(ABC):
    @property
    @abstractmethod
    def api_key(self): pass        # @abstractmethod MUST be innermost
    @abstractmethod
    def run(self): ...             # '...' (Ellipsis) or 'pass'

from typing import Protocol, runtime_checkable
@runtime_checkable
class Embedder(Protocol):
    def embed(self, text: str) -> list[float]: ...  # Ellipsis (...) = pure signature contract
```

## 🛑 STOP — Self-Check

In `rex = Dog("Rex", 3)`, what does `__init__` do, and what is `self` inside it?

<details><summary>Answer</summary>

`__init__` is the **constructor** — it runs automatically when the instance is created, setting up
the object's initial data (here, storing `name="Rex"` and `age=3`). Inside it, **`self` is the
specific new object being created** (the one that will be called `rex`); assigning `self.name = name`
attaches that data to *this* instance, separate from any other `Dog`.
</details>
