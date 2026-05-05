# Java Beginner Reference — For C/Python Programmers

All examples are grounded in the VRP plugin code you will read and modify.

---

## 1. File and class structure

In Java, **one file = one public class**, and the file name must match the class name exactly.

```java
// File: VRPEvaluator.java
public class VRPEvaluator {
    ...
}
```

- **Python analogy:** like a `.py` file where the module name matters.
- **C analogy:** like a `.c` file paired with a `.h` header, but Java fuses both into one.

Every class starts with a `package` declaration (its namespace) and `import` statements (its includes):

```java
package org.opt4j.CAE.VRP;        // like Python's __init__.py path

import java.util.ArrayList;        // like Python's: from java.util import ArrayList
import com.google.inject.Inject;   // third-party library
```

---

## 2. Types — everything is explicit

Java is statically typed. You declare the type of every variable before using it.

| Java | Python equivalent | C equivalent |
|---|---|---|
| `int x = 5;` | `x = 5` | `int x = 5;` |
| `double d = 3.14;` | `d = 3.14` | `double d = 3.14;` |
| `String s = "hi";` | `s = "hi"` | `char s[] = "hi";` |
| `boolean flag = true;` | `flag = True` | `int flag = 1;` |

**Primitive vs object types:** `int`, `double`, `boolean` are primitives (like C). Their object wrappers are `Integer`, `Double`, `Boolean` — needed when generics are involved (see section 5).

---

## 3. Methods (functions)

```java
// return_type  name  (param_type param_name)
public double distance(Point other) {
    return Math.sqrt(Math.pow(x - other.x, 2) + Math.pow(y - other.y, 2));
}
```

- `public` / `private` / `protected` — visibility (see section 7).
- `void` means no return value (like Python `-> None` or C `void`).
- `@Override` above a method means "I'm replacing the parent class's version of this" — the compiler checks that a matching method actually exists in the parent.

```java
@Override
public PermutationGenotype<Item> create() { ... }
```

---

## 4. Classes and objects

A class is a blueprint. An object is an instance of it.

```java
// Define
public class Point {
    private double x, y;                        // fields (like struct members in C)

    public Point(double x, double y) {          // constructor — same name as class, no return type
        this.x = x;                             // "this" = self in Python
        this.y = y;
    }

    public double getX() { return x; }          // getter
    public void setX(double x) { this.x = x; } // setter
}

// Use
Point p = new Point(3.0, 4.0);   // like Python: p = Point(3.0, 4.0)
double px = p.getX();
```

**Python analogy:** `__init__` is the constructor, `self` is `this`.  
**C analogy:** a class is like a `struct` with functions attached.

---

## 5. Generics — `<T>` placeholders

Generics let a class work with any type, decided at use time. You will see them everywhere.

```java
ArrayList<Double> distances = new ArrayList<Double>();
// Python: distances = []   (but Java knows it holds only doubles)

PermutationGenotype<Item> genotype = new PermutationGenotype<Item>();
// A PermutationGenotype that holds Items specifically
```

Think of `<T>` as a fill-in-the-blank: "a list of ___". The blank is filled when you declare the variable.

---

## 6. Collections — ArrayList

`ArrayList` is Java's dynamic array, equivalent to a Python list.

```java
ArrayList<Double> distances = new ArrayList<Double>();

distances.add(3.14);          // append
distances.get(0);             // distances[0]
distances.size();             // len(distances)
Collections.max(distances);   // max(distances)
Collections.shuffle(list);    // random.shuffle(list)
```

Iterating — two styles:

```java
// For-each (like Python's for item in list)
for (VRPRoute route : vprRoutes) {
    // use route
}

// Index-based (like C's for loop)
for (int i = 0; i < route.size(); i++) {
    Point p = route.get(i);
}
```

---

## 7. Visibility modifiers

| Keyword | Who can access it |
|---|---|
| `public` | Anyone |
| `private` | Only this class |
| `protected` | This class + subclasses |
| *(none)* | Only classes in the same package |

You will see `protected` on fields in `VRPModule` — subclasses (your modified versions) can read them directly.

---

## 8. Inheritance and interfaces

**Inheritance** (`extends`) — like Python's class Child(Parent):

```java
public class VRPRoutes extends ArrayList<VRPRoute> {
    // VRPRoutes IS an ArrayList<VRPRoute> plus anything we add
}
```

**Interface** (`implements`) — a contract: "this class guarantees it has these methods". Like Python's abstract base classes but stricter.

```java
public class VRPEvaluator implements Evaluator<VRPRoutes> {
    // MUST implement all methods declared in Evaluator<VRPRoutes>
    @Override
    public Objectives evaluate(VRPRoutes routes) { ... }
}
```

- `extends` = inherit from one parent class (Java allows only one).
- `implements` = fulfill one or more interfaces (can have many).

---

## 9. `instanceof` and casting

`instanceof` checks the runtime type of an object — like Python's `isinstance()`.

```java
if (item instanceof Vehicle) {
    // item is confirmed to be a Vehicle here
    Vehicle v = (Vehicle) item;   // cast: tell Java "treat it as Vehicle"
    int id = v.getId();
}
```

In VRPDecoder, `Item` is the abstract parent of both `Client` and `Vehicle`. The chromosome holds a mix of both; `instanceof` separates them.

**Python analogy:**
```python
if isinstance(item, Vehicle):
    v = item   # no cast needed in Python
```

---

## 10. Abstract classes and inner classes

**Abstract class** — cannot be instantiated directly; exists only to be extended.

```java
public abstract class Item {}   // you can't do: new Item()
public class Vehicle extends Item { ... }
public class Client  extends Item { ... }
```

**Inner class** — a class defined inside another class. It has access to the outer class's fields.

```java
public class VRPProblem {
    public abstract class Item {}        // inner — belongs to VRPProblem
    public class Vehicle extends Item {} // inner subclass
    public class Client  extends Item {} // inner subclass
}
```

To reference an inner class from outside: `VRPProblem.Item`, `VRPProblem.Vehicle`, etc. — which is why you see those imports in VRPDecoder:

```java
import org.opt4j.CAE.VRP.VRPProblem.Vehicle;
import org.opt4j.CAE.VRP.VRPProblem.Client;
import org.opt4j.CAE.VRP.VRPProblem.Item;
```

---

## 11. `final` keyword

`final` on a field means it cannot be reassigned after the constructor sets it — like Python's convention of treating something as a constant, but enforced by the compiler.

```java
protected final VRPProblem problem;   // set once in constructor, never changed
```

`final` on a class means it cannot be subclassed.

---

## 12. Annotations — `@Something`

Annotations are metadata tags read by frameworks at runtime. You don't write annotations yourself often, but you need to understand what the ones in this project do.

| Annotation | What it does |
|---|---|
| `@Inject` | Tells Guice: "call this constructor and inject the arguments automatically" |
| `@Constant(value="key")` | Binds a field to a named config value (GUI parameter or XML property) |
| `@Override` | Compiler check: "this method must exist in the parent" |
| `@Parent(X.class)` | Opt4J GUI: place this module under category X |
| `@File` | Opt4J GUI: render this String field as a file picker |

`@Inject` is the most important one for this project. When Guice sees:

```java
@Inject
public VRPCreator(VRPProblem problem) {
    this.problem = problem;
}
```

It automatically creates a `VRPProblem` instance and passes it in — you never call `new VRPCreator(...)` yourself. This is dependency injection: the framework builds the object graph for you.

---

## 13. `null` and common pitfalls

`null` means "no object" — like Python's `None`. Calling a method on `null` crashes with `NullPointerException` (the most common Java runtime error).

```java
String s = null;
s.length();   // NullPointerException — like AttributeError on None in Python
```

Always initialize fields or check before use.

---

## 14. The `%` operator and wrap-around indexing

You will see this pattern in VRPEvaluator:

```java
Point two = route.get((i + 1) % route.size());
```

`%` is modulo, same as Python and C. `(i+1) % size` wraps around: when `i` is the last index, `i+1` equals `size`, and `size % size = 0` — back to the first element. This creates a circular loop over the route.

---

## 15. Quick syntax cheat sheet

| Concept | Java | Python |
|---|---|---|
| Print | `System.out.println("hi");` | `print("hi")` |
| String concat | `"hello " + name` | `f"hello {name}"` |
| Null check | `if (x == null)` | `if x is None` |
| Integer division | `5 / 2 → 2` | `5 // 2 → 2` |
| Float division | `5.0 / 2 → 2.5` | `5 / 2 → 2.5` |
| Ternary | `x > 0 ? x : -x` | `x if x > 0 else -x` |
| Array (fixed) | `int[] arr = new int[10];` | `arr = [0]*10` |
| Cast | `(int) 3.9 → 3` | `int(3.9) → 3` |
| Math sqrt | `Math.sqrt(x)` | `math.sqrt(x)` |
| Math power | `Math.pow(x, 2)` | `x**2` |

---

## 16. Compilation — how Java code becomes a runnable plugin

This section explains what actually happens when you run the compile command, step by step.

### The big picture

In Python you just run the `.py` file directly — the interpreter reads it on the fly. Java does not work that way. There are two separate stages:

1. **Compile** — `javac` reads your `.java` files and produces `.class` files (bytecode).
2. **Run** — the Java Virtual Machine (JVM) executes the `.class` files.

You never run `.java` files directly. What Opt4J loads is always a `.class` file, packaged inside a `.jar`.

---

### What is a `.class` file?

When `javac` compiles `VRPEvaluator.java` it produces `VRPEvaluator.class`. This is not machine code like C produces — it is **bytecode**, a compact binary format that the JVM understands. It is platform-independent: the same `.class` runs on Windows, Linux, and Mac as long as a JVM is installed.

**Python analogy:** similar to `.pyc` files that Python generates automatically, except in Java you must trigger the compilation yourself.

---

### What is a `.jar` file?

A JAR (Java ARchive) is just a **zip file** containing `.class` files, organized in a folder structure that mirrors the package names.

Inside `VRP_XL.jar` the structure looks like:

```
org/
└── opt4j/
    └── CAE/
        └── VRP/
            ├── DronesModule.class
            ├── VRPCreator.class
            ├── VRPDecoder.class
            └── ...
```

Opt4J scans every `.class` in the JAR at startup to discover your plugin. The folder path inside the JAR must match the `package` declaration in the source — that is why `package org.opt4j.CAE.VRP` produces files nested under `org/opt4j/CAE/VRP/`.

---

### The classpath — "where do I find other classes?"

When compiling, `javac` needs to know where to find classes that your code references but that you did not write yourself — like `ArrayList`, `Evaluator`, `ProblemModule`, etc. These live in JARs that you point to via the **classpath**.

Think of it like Python's `sys.path` or C's include path — it tells the compiler where to look.

In the compile command:

```bash
LIBPATH=$(pwd)/opt4j/lib
CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')opt4j/plugins/CAE_TSP_CSV.jar
```

- `$(ls $LIBPATH/*.jar | tr '\n' ':')` — lists every JAR in `opt4j/lib/` and joins them with `:` (the separator Java uses between classpath entries).
- `opt4j/plugins/CAE_TSP_CSV.jar` — appended at the end because `CAEModule` (the GUI parent category) lives there.

The result is one long string like:

```
opt4j/lib/opt4j-core.jar:opt4j/lib/guice.jar:...:opt4j/plugins/CAE_TSP_CSV.jar
```

`javac` will look inside all of those JARs when it needs to resolve a class you imported.

---

### The compile command — line by line

```bash
find plugin_src/drones/src -name "*.java" > /tmp/sources.txt
```

`find` walks the `src/` folder recursively and collects every `.java` file path into a text file. This is just a convenient way to pass many file names to `javac` at once.

```bash
javac -source 8 -target 8 -cp "$CLASSPATH" @/tmp/sources.txt -d /tmp/vrp_bin/
```

- `-source 8 -target 8` — compile for Java 8. The bundled Windows JRE is Java 8, so the bytecode must match. Using a newer version would crash on Windows with `UnsupportedClassVersionError`.
- `-cp "$CLASSPATH"` — the classpath built above.
- `@/tmp/sources.txt` — the `@` prefix means "read the file list from this file". Same as passing all the `.java` paths directly.
- `-d /tmp/vrp_bin/` — output directory for the `.class` files. `javac` creates the `org/opt4j/...` folder structure inside it automatically.

---

### The packaging command — line by line

```bash
jar cf opt4j/plugins/VRP_XL.jar -C /tmp/vrp_bin/ .
```

- `jar` — the tool that creates JAR files (bundled with the JDK, same as `zip` but Java-aware).
- `c` — create a new archive.
- `f opt4j/plugins/VRP_XL.jar` — name of the JAR to create (overwrites if it exists).
- `-C /tmp/vrp_bin/ .` — this is the critical part. `-C folder .` means "change into `folder` first, then add everything (`.`) from there". Without `-C`, the JAR would contain `tmp/vrp_bin/org/...` — the full absolute path — and Opt4J would not find the classes. With `-C`, the JAR contains `org/...` starting from the root, which is correct.

---

### What happens if you only change one file?

You do not need to recompile everything every time. If you only edited `VRPEvaluator.java`, you can compile just that one file:

```bash
javac -source 8 -target 8 -cp "$CLASSPATH" \
    src/Drones/org/opt4j/CAE/VRP/VRPEvaluator.java \
    -d /tmp/vrp_bin/
```

This replaces only `VRPEvaluator.class` in `/tmp/vrp_bin/`. Then repackage the JAR as normal — `jar cf` overwrites the whole JAR with whatever is in `/tmp/vrp_bin/` at that moment, so all other classes are still there from the previous full compile.

---

### Common compile errors and what they mean

| Error message | What went wrong | Fix |
|---|---|---|
| `cannot find symbol` | You referenced a class or method that javac cannot locate | Check imports and classpath |
| `class X is public, should be in file X.java` | File name does not match class name | Rename one to match the other |
| `reached end of file while parsing` | A `{` was opened but never closed | Find the missing `}` |
| `UnsupportedClassVersionError` (at runtime) | Compiled for Java > 8 but JRE is Java 8 | Ensure `-source 8 -target 8` was used |
| `package X does not exist` | An import points to a class not on the classpath | Add the right JAR to `-cp` |

---

## 17. The compile.sh script — line by line

This is the full script you run to build the Drones plugin:

```bash
#!/bin/bash
set -e

LIBPATH=$(pwd)/lib
CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')

mkdir -p /tmp/vrp_bin

find src/Drones -name "*.java" > /tmp/sources.txt
javac -source 8 -target 8 -cp "$CLASSPATH" @/tmp/sources.txt -d /tmp/vrp_bin/

jar cf plugins/Drones.jar -C /tmp/vrp_bin/ .

echo "Done — plugins/Drones.jar updated"
```

---

### `#!/bin/bash`

The **shebang** — tells the operating system which interpreter to use when you run this file. Without it, the OS wouldn't know it's a bash script.

**Python analogy:** like `#!/usr/bin/env python3` at the top of a Python script.

---

### `set -e`

Tells bash: **stop immediately if any command fails**. Without this, if `javac` fails with an error, bash would keep going and package a broken or empty JAR anyway. With `set -e`, it stops at the first failure so you see the actual error.

---

### `LIBPATH=$(pwd)/lib`

- `$(pwd)` — runs the `pwd` command ("print working directory") and inserts its output inline. So if you're in `/home/user/opt4j`, this becomes `/home/user/opt4j/lib`.
- The result is stored in the variable `LIBPATH`.

**Why not hardcode the path?** Because `$(pwd)` makes it work from any machine, any user, any location — as long as you run the script from inside `opt4j/`.

---

### `CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')`

Three things chained together:

- `ls $LIBPATH/*.jar` — lists every `.jar` file in `lib/`, one per line.
- `|` — **pipe**: takes the output of the left command and feeds it as input to the right command.
- `tr '\n' ':'` — **translate**: replaces every newline (`\n`) with a colon (`:`). This turns the list of JAR paths into a single colon-separated string, which is the format Java expects for the classpath.

**Python analogy:** `':'.join(jars)` — joining a list with a separator.

---

### `mkdir -p /tmp/vrp_bin`

Creates the output directory for compiled `.class` files.

- `/tmp/` — a temporary folder that Linux provides for scratch work, cleared on reboot.
- `-p` — "parents": creates any missing parent directories without error, and does nothing if the folder already exists.

---

### `find src/Drones -name "*.java" > /tmp/sources.txt`

- `find src/Drones -name "*.java"` — recursively finds every `.java` file under `src/Drones/`.
- `>` — **redirect**: instead of printing to the terminal, writes the output to the file `/tmp/sources.txt`.

The result is a text file with one `.java` path per line — passed to `javac` in the next step.

---

### `javac -source 8 -target 8 -cp "$CLASSPATH" @/tmp/sources.txt -d /tmp/vrp_bin/`

- `javac` — the Java compiler.
- `-source 8 -target 8` — compile for Java 8 bytecode (required by the bundled Windows JRE).
- `-cp "$CLASSPATH"` — the classpath: where to find external classes your code references.
- `@/tmp/sources.txt` — the `@` prefix means "read arguments from this file". Equivalent to listing all `.java` files directly on the command line.
- `-d /tmp/vrp_bin/` — output directory for `.class` files. `javac` recreates the `org/opt4j/...` folder structure inside it automatically.

---

### `jar cf plugins/Drones.jar -C /tmp/vrp_bin/ .`

- `jar` — the tool that creates JAR files (like `zip` but for Java).
- `c` — **create** a new archive.
- `f plugins/Drones.jar` — the name and location of the JAR to create.
- `-C /tmp/vrp_bin/ .` — **critical**: "change into `/tmp/vrp_bin/` first, then add everything (`.`) from there". This ensures the JAR contains `org/opt4j/...` at the root, not `tmp/vrp_bin/org/opt4j/...`. Opt4J requires the `org/` folder to be at the root of the JAR.

---

### `echo "Done — plugins/Drones.jar updated"`

Prints a confirmation message to the terminal so you know the script completed successfully.

---

## 18. Reading a class — checklist

When you open a `.java` file you have never seen before, read it in this order:

1. `package` — which namespace is this in?
2. `extends` / `implements` — what is its parent / what contract does it fulfill?
3. Fields at the top — what data does it hold?
4. Constructor (`@Inject` one if present) — how is it built and what does it receive?
5. The main method (`create`, `decode`, `evaluate`, `config`) — the core logic.
6. Private helpers at the bottom — utility methods called by the main method.
