# Opt4J Module Reference — Architecture and Structure

For the step-by-step workflow to edit, compile, and deploy a plugin see [module_workflow.md](module_workflow.md).

---

## How a plugin fits into Opt4J

Opt4J uses **Google Guice** (dependency injection) to wire everything together. A plugin is a JAR placed in `opt4j/plugins/`. At startup Opt4J scans that folder, finds every class that extends `Opt4JModule`, and exposes it in the GUI configurator.

A complete plugin for a combinatorial problem needs six things:

| Class | Role |
|---|---|
| **Problem** | Stores the problem data (clients, vehicles, etc.) |
| **Creator** | Generates a random initial genotype (chromosome) |
| **Decoder** | Converts genotype → phenotype (interpretable solution) |
| **Evaluator** | Computes objective values from the phenotype |
| **ProblemModule** | Guice module: wires the four above and exposes GUI params |
| **VisualizationModule** *(optional)* | Registers a Swing widget for the viewer |

---

## Data flow

```
GUI params (XML/panel)
        │  @Constant fields in ProblemModule
        ▼
  VRPModule.config()
        │  bindProblem(Creator, Decoder, Evaluator)
        ▼
  VRPProblem ──(@Inject)──► VRPCreator ──► PermutationGenotype<Item>
                                                       │
                            VRPDecoder ◄───────────────┘
                                │
                            VRPRoutes  (phenotype)
                                │
                            VRPEvaluator
                                │
                            Objectives { max_distance MIN, num_vehicles MIN }
```

Guice creates **one shared instance** of `VRPProblem` and injects it into Creator, Decoder, and any other class that needs it.

---

## Problem class — `VRPProblem`

Models the problem data. Constructed once by Guice; shared with Creator and Decoder.

```java
public class VRPProblem {
    protected ArrayList<Item> clients = new ArrayList<>();
    protected ArrayList<Item> vehicles = new ArrayList<>();
    protected int totalVehicles;
    protected Client base;      // (0,0) — the depot

    // Abstract base for Client and Vehicle
    public abstract class Item {}

    public class Vehicle extends Item {
        private int id;
        public Vehicle(int id) { this.id = id; }
        public int getId() { return id; }
    }

    public class Client extends Item {
        protected final Point p;
        public Client(double x, double y) { this.p = new Point(x, y); }
        public Point getPoint() { return p; }
    }

    @Inject
    public VRPProblem(
            @Constant(value = "clientes")       int size,
            @Constant(value = "vehiculos")      int totalVehicles,
            @Constant(value = "nombre fichero") String fileName) {

        base = new Client(0, 0);

        if (fileName.length() > 0)
            readInstance(fileName);   // load from CSV
        else {
            Random random = new Random(0);
            for (int i = 0; i < size; i++)
                clients.add(new Client(random.nextDouble() * 100,
                                       random.nextDouble() * 100));
        }

        this.totalVehicles = totalVehicles;
        for (int x = 0; x < totalVehicles; x++)
            vehicles.add(new Vehicle(x));
    }
}
```

**Key points:**
- `@Inject` on the constructor tells Guice to call it.
- `@Constant(value = "key")` binds each parameter to the GUI field whose `@Constant` has the matching key (defined in `VRPModule`).
- `Item` is abstract; `Client` and `Vehicle` extend it so a single `PermutationGenotype<Item>` can hold both.
- Vehicle 0 is implicit — only vehicles 1..N are added to the genotype (see Creator).

**Beginner breakdown:**

`protected ArrayList<Item> clients = new ArrayList<>()` — declares a list of `Item` objects called `clients`. `protected` means subclasses can access it directly. The `= new ArrayList<>()` initializes it immediately so it's never null.

`public abstract class Item {}` — an abstract inner class. It has no fields or methods — it exists only as a common type label so that `Client` and `Vehicle` can be stored together in the same list. You cannot do `new Item()` — it's just a category.

`public class Vehicle extends Item` — `Vehicle` is a concrete subclass of `Item`. It adds an `id` field. `extends` means "Vehicle IS an Item, plus it has an id".

`@Inject public VRPProblem(...)` — the `@Inject` annotation tells Guice: "when you need a `VRPProblem`, call this constructor". Guice then looks at each parameter annotated with `@Constant(value="key")` and fills them in from the GUI values. You never call `new VRPProblem(...)` yourself.

`if (fileName.length() > 0)` — checks whether the user provided a CSV file in the GUI. `length() > 0` means the string is not empty. If empty, random clients are generated instead.

`new Random(0)` — creates a random number generator with seed `0`. Using a fixed seed means the same random clients are generated every run — useful for reproducibility.

`random.nextDouble() * 100` — generates a random decimal between 0.0 and 100.0. This places clients randomly in a 100×100 grid.

---

## Creator — `VRPCreator`

Generates the initial random chromosome.

```java
public class VRPCreator implements Creator<PermutationGenotype<Item>> {
    protected final VRPProblem problem;

    @Inject
    public VRPCreator(VRPProblem problem) {
        this.problem = problem;
    }

    @Override
    public PermutationGenotype<Item> create() {
        PermutationGenotype<Item> genotype = new PermutationGenotype<>();
        for (Item item : problem.getClients())
            genotype.add(item);                        // all clients
        for (int x = 1; x < problem.getVehicles().size(); x++)
            genotype.add(problem.getVehicles().get(x)); // vehicles 1..N (not 0)
        Collections.shuffle(genotype);
        return genotype;
    }
}
```

**Key points:**
- Vehicle 0 is always implicit at the start of the route; only vehicles 1..N go into the permutation.
- `PermutationGenotype<Item>` is an `ArrayList<Item>` that the EA operators know how to shuffle/crossover while maintaining a valid permutation.

**Beginner breakdown:**

`implements Creator<PermutationGenotype<Item>>` — this class fulfills the `Creator` interface, specifically one that produces a `PermutationGenotype<Item>`. The `<Item>` inside means the permutation holds objects of type `Item` (which are either `Client` or `Vehicle` at runtime).

`protected final VRPProblem problem` — a field that holds a reference to the problem instance. `final` means it can only be set once (in the constructor) and never changed after. `protected` means subclasses can access it.

`@Inject public VRPCreator(VRPProblem problem)` — Guice calls this constructor and passes in the already-created `VRPProblem` instance. This is how `VRPCreator` gets access to the list of clients and vehicles without creating a new problem itself.

`for (Item item : problem.getClients())` — a for-each loop over all clients. `problem.getClients()` returns the `ArrayList<Item>` of clients. Each iteration gives one `Item` (which is actually a `Client`) stored in `item`.

`for (int x = 1; x < problem.getVehicles().size(); x++)` — a classic index loop starting at `1`, not `0`. Vehicle 0 is skipped because it is implicit — it always starts the first route automatically in the decoder.

`Collections.shuffle(genotype)` — randomly reorders all elements in the list. This is how the initial population gets diversity — every call to `create()` produces a different random ordering.

---

## Decoder — `VRPDecoder`

Converts a chromosome into a concrete solution (set of routes).

```java
public class VRPDecoder implements Decoder<PermutationGenotype<Item>, VRPRoutes> {
    protected final VRPProblem problem;

    @Inject
    public VRPDecoder(VRPProblem problem) { this.problem = problem; }

    @Override
    public VRPRoutes decode(PermutationGenotype<Item> genotype) {
        VRPRoutes routes = new VRPRoutes();
        VRPRoute current = newRoute(0);   // vehicle 0 always starts first
        routes.add(current);

        for (Item item : genotype) {
            if (item instanceof Vehicle) {
                endRoute(current);
                current = newRoute(((Vehicle) item).getId());
                routes.add(current);
            } else {
                current.add(((Client) item).getPoint());
            }
        }
        endRoute(current);
        return routes;
    }

    private VRPRoute newRoute(int id) {
        VRPRoute r = new VRPRoute(id);
        r.add(problem.getBase().getPoint());  // start at depot
        return r;
    }

    private VRPRoute endRoute(VRPRoute r) { return r; }  // depot implicit
}
```

**Decoding logic (left-to-right scan):**

```
Chromosome:  [C3, C1, V2, C5, C2, V1, C4]

Vehicle 0 (implicit):   depot → C3 → C1 → depot
Vehicle 2:              depot → C5 → C2 → depot
Vehicle 1:              depot → C4 → depot
```

Vehicles in the chromosome act as dividers. Clients between two vehicle tokens belong to the left vehicle's route.

**Beginner breakdown:**

`implements Decoder<PermutationGenotype<Item>, VRPRoutes>` — this class takes a `PermutationGenotype<Item>` as input and produces a `VRPRoutes` as output. The two type parameters say exactly what goes in and what comes out.

`VRPRoutes routes = new VRPRoutes()` — creates an empty list of routes (the phenotype). Routes are added to this as the chromosome is scanned.

`for (Item item : genotype)` — scans the chromosome left to right, one element at a time. Each element is either a `Vehicle` (route divider) or a `Client` (waypoint to add to the current route).

`if (item instanceof Vehicle)` — checks whether the current element is a `Vehicle`. If yes, the current route is closed and a new one is started. If no, it must be a `Client`, so its coordinates are added to the current route.

`((Vehicle) item).getId()` — casts `item` from `Item` to `Vehicle` so we can call `getId()`. The cast is safe here because `instanceof` already confirmed it is a `Vehicle`.

`((Client) item).getPoint()` — same pattern: cast to `Client` to access `getPoint()`, which returns the `Point` (x,y coordinate) to add to the current route.

`private VRPRoute newRoute(int id)` — a private helper method. `private` means only `VRPDecoder` itself can call it. It creates a new route and adds the depot as the first waypoint.

`private VRPRoute endRoute(VRPRoute r) { return r; }` — does nothing currently (the depot return is implicit in the circular distance calculation in the Evaluator). It exists as a hook in case you want to add closing logic later.

---

## Evaluator — `VRPEvaluator`

Computes objective values from the phenotype. Does **not** need `@Inject` if it uses no shared state.

```java
public class VRPEvaluator implements Evaluator<VRPRoutes> {

    @Override
    public Objectives evaluate(VRPRoutes routes) {
        ArrayList<Double> distances = new ArrayList<>();
        int nVehicles = 0;

        for (VRPRoute route : routes) {
            double d = 0;
            for (int i = 0; i < route.size(); i++) {
                Point a = route.get(i);
                Point b = route.get((i + 1) % route.size());
                d += a.distance(b);
            }
            distances.add(d);
            if (d > 0) nVehicles++;
        }

        Objectives obj = new Objectives();
        obj.add("max_distance", Sign.MIN, Collections.max(distances));
        obj.add("num_vehicles", Sign.MIN, nVehicles);
        return obj;
    }
}
```

**Key points:**
- `Objectives.add(name, sign, value)` — the name appears as a column header in `output.tsv`.
- `Sign.MIN` / `Sign.MAX` — whether to minimize or maximize.
- Routes wrap around: `(i+1) % route.size()` computes distance back to the depot (which is `route.get(0)`).
- `nVehicles` counts only routes with distance > 0 (vehicles that actually moved).

**Beginner breakdown:**

`implements Evaluator<VRPRoutes>` — this class receives a `VRPRoutes` phenotype and returns an `Objectives` object. No `@Inject` needed because the evaluator uses no shared state — it only reads the routes passed to it.

`ArrayList<Double> distances = new ArrayList<>()` — a local list (created fresh every call) to collect the total distance of each route. Used at the end to find the maximum.

`for (VRPRoute route : routes)` — outer loop: iterates over each vehicle's route.

`for (int i = 0; i < route.size(); i++)` — inner loop: iterates over each waypoint in the route by index, so we can access the next waypoint with `i+1`.

`route.get((i + 1) % route.size())` — gets the next waypoint. The `%` (modulo) wraps around: when `i` is the last index, `i+1` would be out of bounds, but `% route.size()` brings it back to `0` (the depot). This closes the route back to the start.

`d += a.distance(b)` — accumulates the Euclidean distance between consecutive points. `+=` means "add to the existing value of d".

`if (d > 0) nVehicles++` — only counts a vehicle as "used" if it actually traveled somewhere. Vehicles with empty routes have distance 0.

`obj.add("max_distance", Sign.MIN, Collections.max(distances))` — registers the first objective. `Collections.max()` finds the largest value in the distances list. `Sign.MIN` tells the optimizer to minimize this value. The string `"max_distance"` becomes the column name in the output TSV file.

---

## Phenotype classes

### `Point`

```java
public class Point {
    private double x, y;
    public Point(double x, double y) { this.x = x; this.y = y; }
    public double distance(Point other) {
        return Math.sqrt(Math.pow(x - other.x, 2) + Math.pow(y - other.y, 2));
    }
}
```

### `VRPRoute extends ArrayList<Point>`

One vehicle's ordered list of waypoints (starts with the depot `Point`).

```java
public class VRPRoute extends ArrayList<Point> {
    private int vehicleId;
    public VRPRoute(int vehicleId) { this.vehicleId = vehicleId; }
}
```

### `VRPRoutes extends ArrayList<VRPRoute>`

The complete phenotype — one `VRPRoute` per vehicle.

---

## ProblemModule — `VRPModule`

Wires everything together and exposes the GUI configuration panel.

```java
@Parent(CAEModule.class)          // places this module under "CAE" in the GUI tree
public class VRPModule extends ProblemModule {

    @Constant(value = "vehiculos")
    protected int totalVehicles = 10;

    @Constant(value = "clientes")
    protected int clients = 100;

    @Constant(value = "nombre fichero")
    @File
    protected String fileName = "";

    // Standard Java getters and setters required for GUI binding
    public int getTotalVehicles()              { return totalVehicles; }
    public void setTotalVehicles(int v)        { totalVehicles = v; }
    public int getClients()                    { return clients; }
    public void setClients(int v)              { clients = v; }
    public String getFileName()                { return fileName; }
    public void setFileName(String v)          { fileName = v; }

    @Override
    public void config() {
        bindProblem(VRPCreator.class, VRPDecoder.class, VRPEvaluator.class);
    }
}
```

**Key points:**
- `@Constant(value = "key")` on a field does two things: exposes the field as an editable parameter in the GUI panel, and makes the value injectable via `@Constant("key")` in `VRPProblem`'s constructor. The string key must match exactly.
- `@File` on a String field turns it into a file-picker widget in the GUI.
- `bindProblem(Creator, Decoder, Evaluator)` tells Guice which implementations to use.
- Getter/setter names must follow standard Java convention (`getFieldName` / `setFieldName`) — the GUI reflectively calls them.
- `@Parent(CAEModule.class)` places this panel under the CAE category node in the GUI module tree.

**Beginner breakdown:**

`extends ProblemModule` — `DronesModule` inherits from `ProblemModule`, which is part of the Opt4J framework. This inheritance is what makes Opt4J recognize it as a plugin module and show it in the GUI.

`@Parent(CAEModule.class)` — tells Opt4J's GUI to place this module inside the "CAE" category folder. Without this, the module would appear at the top level with no category.

`@Constant(value = "vehiculos") protected int totalVehicles = 10` — three things at once: `@Constant` registers this field with the DI system under the key `"vehiculos"`; `protected` makes it accessible to subclasses; `= 10` sets the default value shown in the GUI.

`public int getTotalVehicles() { return totalVehicles; }` — a getter. The GUI calls this method (by reflection — it looks for methods named `get` + field name) to read the current value and display it in the panel.

`public void setTotalVehicles(int v) { totalVehicles = v; }` — a setter. The GUI calls this when the user changes the value in the panel.

`@File protected String fileName = ""` — `@File` is an Opt4J annotation that turns this String field into a file-picker button in the GUI instead of a plain text box.

`@Override public void config()` — this method is called by Opt4J during setup. `@Override` confirms it overrides the parent's `config()`. Inside it, `bindProblem()` registers which Creator, Decoder, and Evaluator to use — this is the wiring step that connects all four core classes together.

### `@Constant` vs `@Name`

| Annotation | What it controls |
|---|---|
| `@Constant(value = "key")` | The XML property key and the DI binding key — not the GUI label |
| `@Name("label")` | The label shown next to the field in the GUI panel |

Both can be on the same field: `@Constant` links the value to the XML/DI system; `@Name` just changes how it looks in the GUI.

---

## VisualizationModule — `VRPWidgetModule`

Optional. Registers a Swing panel that appears in the Opt4J viewer when you click on an individual.

```java
public class VRPWidgetModule extends VisualizationModule {
    @Override
    public void config() {
        addIndividualMouseListener(VRPWidgetService.class);
    }
}
```

- Does **not** need `@Parent` — Opt4J places it automatically in the Viewer section.
- `VRPWidgetService` implements the Swing drawing logic; it receives the clicked phenotype and renders it.

---

## GUI category annotations

| Annotation | Where | Effect |
|---|---|---|
| `@Category` | On a class | Declares that class as a tree node (not a module) |
| `@Parent(X.class)` | On a module class | Places the module under category `X` in the GUI tree |
| `@Name("label")` | On any class or field | Overrides the display name (otherwise full class name is shown) |
| `@Icon(Icons.XYZ)` | On a category class | Sets the icon for that tree node |

`CAEModule` is the shared root category used by all course plugins:

```java
@Category
@Icon(Icons.HELP)
public final class CAEModule {}
```

---

## XML configuration and `@Constant` keys

The XML config mirrors the `@Constant` values exactly:

```xml
<module class="org.opt4j.CAE.VRP.VRPModule">
    <property name="vehiculos">10</property>
    <property name="clientes">100</property>
    <property name="nombre fichero"></property>
</module>
```

The `name` attribute must match the `@Constant(value = "...")` string on the field in `VRPModule`.

---

## Editing — Adding a GUI parameter

To add a new configurable parameter (e.g. `droneSpeed`):

**1. Add the field to `VRPModule.java`:**

```java
@Constant(value = "drone speed")
protected double droneSpeed = 1.5;

public double getDroneSpeed()          { return droneSpeed; }
public void setDroneSpeed(double v)    { droneSpeed = v; }
```

**2. Inject it into the class that needs it (e.g. `VRPEvaluator.java`):**

```java
private final double droneSpeed;

@Inject
public VRPEvaluator(@Constant(value = "drone speed") double droneSpeed) {
    this.droneSpeed = droneSpeed;
}
```

**3. Use it in the XML config:**

```xml
<property name="drone speed">1.5</property>
```

The string in `@Constant(value = "...")` must match exactly across all three places.

To change the GUI label without changing the binding key:

```java
@Constant(value = "drone speed")
@Name("Drone speed (m/s)")
protected double droneSpeed = 1.5;
```

---

## Editing — Adding a new objective

In `VRPEvaluator.java`, add another line in `evaluate()`:

```java
objectives.add("total_distance", Sign.MIN, totalDist);
```

The string label becomes a column header in `output.tsv`. Use `Sign.MIN` to minimize, `Sign.MAX` to maximize.

---

## Compilation — Compile a single file

If you only changed one file, compile only that file — faster than recompiling everything:

```bash
# run from inside opt4j/
LIBPATH=$(pwd)/lib
CLASSPATH=$(ls $LIBPATH/*.jar | tr '\n' ':')

javac -source 8 -target 8 -cp "$CLASSPATH" \
    src/Drones/org/opt4j/CAE/VRP/VRPEvaluator.java \
    -d /tmp/vrp_bin/
```

Then repackage (`jar cf plugins/Drones.jar -C /tmp/vrp_bin/ .`) and sync.

---

## Class summary

```
VRPProblem        stores clients (ArrayList<Item>), vehicles (ArrayList<Item>), base point
  ├─ Item         abstract inner class — common type for Client and Vehicle
  ├─ Client       extends Item — has a Point (x,y coordinate)
  └─ Vehicle      extends Item — has an id (used as route divider in chromosome)

VRPCreator        implements Creator<PermutationGenotype<Item>>
                  shuffles all clients + vehicles[1..N] into a random permutation

VRPDecoder        implements Decoder<PermutationGenotype<Item>, VRPRoutes>
                  scans chromosome left-to-right; Vehicle token = start new route

VRPEvaluator      implements Evaluator<VRPRoutes>
                  max_distance [MIN], num_vehicles [MIN]

VRPRoute          extends ArrayList<Point> — one vehicle's waypoints (starts at depot)
VRPRoutes         extends ArrayList<VRPRoute> — the full phenotype

Point             (x,y) with Euclidean distance()

VRPModule         extends ProblemModule — GUI params + bindProblem()
VRPWidgetModule   extends VisualizationModule — registers VRPWidgetService
```

---

## Drones extension — changes from baseline VRP

This section documents the modifications made to the `Drones` plugin to support sweep-based drone routing (barridos).

### VRPProblem — new `Swept` inner class

Added `Swept extends Client` below the `Client` class. A sweep is a client with two coordinates (start and end of a sweep pass).

```java
public class Swept extends Client {
    protected final Point p2;

    public Swept(double x, double y, double x2, double y2) {
        super(x, y);          // p inherited from Client
        this.p2 = new Point(x2, y2);
    }

    public double getY2()       { return p2.getY(); }
    public Point getPoint2()    { return p2; }

    @Override
    public String toString() {
        return String.format("[%s,%s]", getPoint(), getPoint2());
    }
}
```

Also added a second file parameter and `readCS()` method to load the control station from a CSV instead of defaulting to (0,0):

```java
@Inject
public VRPProblem(..., @Constant(value = "nombre fichero CS") String fileNameCS) {
    if (fileNameCS.length() > 0)
        readCS(fileNameCS);
    else
        base = new Client(0, 0);
    ...
}

private void readCS(String fileNameCS) { ... }
```

**Class hierarchy after change:**
```
Item (abstract)
├── Vehicle
└── Client
    └── Swept    ← new
```

### VRPCreator — no changes

`Swept` is a subclass of `Client`, so it already appears in `problem.getClients()`. The creator adds all clients to the genotype without knowing their concrete type — `Swept` instances are picked up automatically.

### VRPDecoder — Swept decoding logic

The `else` branch (non-Vehicle gene) was updated to handle `Swept` specially. Instead of adding one point, it adds both endpoints in order of proximity to the drone's current position:

```java
} else {
    if (item instanceof Swept) {
        Point current = vprRoute.get(vprRoute.size() - 1);
        Point p1 = ((Swept) item).getPoint();
        Point p2 = ((Swept) item).getPoint2();
        if (current.distance(p1) < current.distance(p2)) {
            vprRoute.add(p1);
            vprRoute.add(p2);
        } else {
            vprRoute.add(p2);
            vprRoute.add(p1);
        }
    } else throw new RuntimeException("Tipo incorrecto de gen en decode()");
}
```

`RuntimeException` is used (not `Exception`) because `decode()` comes from the Opt4J interface which does not declare `throws Exception`.

Also added the import:
```java
import org.opt4j.CAE.VRP.VRPProblem.Swept;
```

### VRPEvaluator — no changes

The evaluator operates on `VRPRoutes` (lists of `Point`). The decoder already converted each `Swept` into two `Point` entries in the route, so the evaluator sees no difference — it just accumulates distances between consecutive points.
