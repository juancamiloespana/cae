# Opt4J Module Workflow — Edit, Compile, and Deploy a Plugin

For architecture, class roles, annotation reference, and how to add parameters or objectives see [module_reference.md](module_reference.md).

---

## Step 1 — Edit the source

Files are in `opt4j/src/Drones/org/opt4j/CAE/VRP/`. Common targets:

| What to change | File |
|---|---|
| Objective formula or new objective | `VRPEvaluator.java` |
| How the chromosome is built | `VRPCreator.java` |
| How the chromosome maps to a solution | `VRPDecoder.java` |
| Problem parameters exposed in the GUI | `DronesModule.java` + `VRPProblem.java` |

---

## Step 2 — Compile

Run from inside `opt4j/`. Verify Java 8 is active first:

```bash
java -version   # must show openjdk version "1.8.0_..."
```

If not: `sdk use java 8.0.482-tem`

Then run the compile script:

```bash
cd opt4j
./compile.sh
```

Output should be empty. Any error includes the file name and line number.

---

## Step 3 — Verify the JAR

```bash
jar tf plugins/Drones.jar | head
```

First lines must start with `org/`, not `tmp/` or `bin/`. If not, the `-C` path in `compile.sh` is wrong.

---

## Step 4 — Sync to Windows and test

```bash
rsync -av --delete /home/personal/cod_lin/CAE_lin/CAE1_lin/ /mnt/d/cod/CAE1_win/
```

Launch `opt4j\bin\opt4j-JVM1.8.bat` on Windows. In the GUI click **Add module** → **CAE** → **Drones** should appear alongside **VRP**.

**If the module does not appear:**

| Symptom | Likely cause | Fix |
|---|---|---|
| CAE category missing | JAR not in `plugins\` | Check folder — not `lib\` |
| Drones not under CAE | Class does not extend `ProblemModule` | Check `DronesModule.java` |
| Java error on launch | Classes compiled for wrong version | Ensure `-source 8 -target 8` was used |

---

## Quick reference — full cycle

```bash
# 1. Edit
nano opt4j/src/Drones/org/opt4j/CAE/VRP/VRPEvaluator.java

# 2. Compile
cd opt4j && ./compile.sh

# 3. Sync
rsync -av --delete /home/personal/cod_lin/CAE_lin/CAE1_lin/ /mnt/d/cod/CAE1_win/
```
