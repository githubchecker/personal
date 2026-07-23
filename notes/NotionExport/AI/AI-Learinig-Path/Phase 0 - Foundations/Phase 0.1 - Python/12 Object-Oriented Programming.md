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
- **`__init__`** — the constructor; runs automatically when you create an instance.
- **`self`** — the current instance, inside a method.
- **Inheritance** — a class building on another; **dunder** — special `__methods__` Python calls for you.

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

### 12.2 Instance vs class attributes

```python
class Dog:
    species = "Canis familiaris"     # CLASS attribute: shared by ALL dogs
    def __init__(self, name):
        self.name = name             # INSTANCE attribute: unique per dog

print(Dog.species)        # shared value, same for every instance
```

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

### 12.4 Dunder methods — make objects behave naturally

"Dunder" = double-underscore methods Python calls automatically in special situations:

```python
class Money:
    def __init__(self, amount):
        self.amount = amount
    def __repr__(self):                  # what you see in the REPL / debugging
        return f"Money({self.amount})"
    def __str__(self):                   # what print() shows to a human
        return f"${self.amount:.2f}"
    def __eq__(self, other):             # defines what "==" means for Money
        return self.amount == other.amount

print(str(Money(5)))           # '$5.00'
print(Money(5) == Money(5))    # True (thanks to __eq__)
```

### 12.5 Properties and class/static methods

```python
class Circle:
    def __init__(self, radius):
        self.radius = radius

    @property                      # call it like an attribute: c.area (no parentheses)
    def area(self):
        return 3.14159 * self.radius ** 2

    @staticmethod                  # no self: a utility grouped under the class
    def from_diameter(d):
        return Circle(d / 2)

c = Circle(2)
print(c.area)                      # 12.566...  — looks like data, computed on the fly
```

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
| `AttributeError: object has no attribute 'x'` | Used `self.x` before it was set | Set it in `__init__` |
| All instances share one list | A mutable **class** attribute | Put per-instance data in `__init__` via `self` |
| Parent setup didn't happen | Subclass `__init__` skipped the parent | Call `super().__init__(...)` |

## 📌 Quick Reference

```python
class Dog(Animal):
    species = "canine"             # class attribute (shared)
    def __init__(self, name):
        super().__init__(name)     # parent setup
        self.name = name           # instance attribute
    def speak(self): return "woof"
    def __repr__(self): return f"Dog({self.name})"

from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
```

## 🛑 STOP — Self-Check

In `rex = Dog("Rex", 3)`, what does `__init__` do, and what is `self` inside it?

<details><summary>Answer</summary>

`__init__` is the **constructor** — it runs automatically when the instance is created, setting up
the object's initial data (here, storing `name="Rex"` and `age=3`). Inside it, **`self` is the
specific new object being created** (the one that will be called `rex`); assigning `self.name = name`
attaches that data to *this* instance, separate from any other `Dog`.
</details>
