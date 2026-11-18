# Mathematical Formulation Guide — Drone-to-Sweep Assignment

This file is a **reference draft** to support feedback on the formulation you build.
It describes the problem structure as understood from the codebase and course context.

**Role:** act as an expert in mathematical formulation and notation — familiar with
combinatorial optimization, multi-objective programming, and standard OR conventions.
Feedback should reflect that expertise: precise, rigorous, and grounded in formal
optimization theory when relevant.

When you share your formulation and ask for feedback, the review will focus on
**mathematical structure and correctness** — not on variable names, which may differ freely.

---

## Task description

The problem is an assignment and routing problem for **drones surveilling a forest**.
The forest area is divided into **sweeps**: linear segments that must each be covered by a drone.
Each sweep has two endpoints; the drone can traverse it in either direction.

The goal is to assign sweeps to drones and plan their routes such that:
- Every sweep is covered by exactly one drone.
- Each drone starts (and returns) from a shared base station.
- Two objectives are optimized simultaneously (multi-objective, Pareto front):
  1. **Minimize the maximum route distance** across all drones (balances workload).
  2. **Minimize the number of active drones** used.

The current implementation in `VRPDecoder` resolves traversal direction greedily
(the endpoint closer to the drone's current position is visited first).

---

## Draft formulation sketch

### Sets
- Drones (vehicles): finite set, cardinality fixed as a parameter.
- Sweeps (clients): finite set, each defined by two spatial endpoints.
- Base station: single depot shared by all drones.

### Parameters
- Euclidean distance function between any two points in 2D space.
- Total number of drones available (upper bound).

### Decision variables (conceptual)
- Assignment of each sweep to a drone.
- Ordering of sweeps within each drone's route.
- Traversal direction chosen for each sweep (which endpoint is entered first).

### Objectives (both minimized)
- `f1`: maximum total distance traveled by any single drone.
- `f2`: number of drones whose total distance is strictly greater than zero.

### Constraints (implicit in permutation encoding)
- Every sweep is assigned to exactly one drone.
- All routes begin and end at the base station (closed tours).
- Number of active drones does not exceed the available fleet.
- No capacity, time-window, or battery constraints in the current base version.

---

## How to use this file

1. Build your formulation independently using your own notation.
2. Share it and ask specific questions (e.g. "is my objective function correct?",
   "is this constraint missing anything?", "does my feasibility condition hold?").
3. Feedback will confirm or correct the **logic and structure** behind what you wrote,
   not the names or symbols you chose.
4. If your formulation extends the base problem (e.g. adds battery limits, time windows,
   speed constraints), flag it explicitly so the feedback accounts for the extension.

---

## Full formulation — Version 1 (2026-05-07)

Saved as backup after first complete review. All constraints verified.

### Índices

- $i \in I$ — índice de drones
- $j \in J$ — índice de puntos: barridos y estación de control ($j=1$ es la CS)
- $k \in K$ — índice del orden de visita de puntos en una ruta

### Parámetros

- $n = |I|$ — número de drones disponibles
- $m = |J| = 2 \times |\text{barridos}| + 1$ — número total de puntos incluyendo CS
- $|K| = m + 1$ — número máximo de posiciones de orden en una ruta
- $c_{j_1 j_2}$ — distancia euclídea entre puntos $j_1$ y $j_2$
- $b_{j_1 j_2} \in \{0,1\}$ — 1 si $j_1$ y $j_2$ son extremos del mismo barrido; simétrica, diagonal cero

### Variable de decisión

- $X_{ijk} \in \{0,1\}$ — 1 si dron $i$ visita punto $j$ en orden $k$

### Variables auxiliares

- $D_i \in \mathbb{R}_{\geq 0}$ — distancia total recorrida por dron $i$
- $U_i \in \{0,1\}$ — 1 si dron $i$ es activo

### Funciones objetivo

- $f_1 = \min \max_{i \in I} D_i$
- $f_2 = \min \sum_{i \in I} U_i$

### Restricciones

1. **Distancia total:** $D_i = \sum_{j_1}\sum_{j_2}\sum_k X_{ij_1k} \cdot X_{ij_2,k+1} \cdot c_{j_1j_2}$
2. **Dron activo (upper):** $U_i \leq \sum_{j \neq 1}\sum_k X_{ijk}$
3. **Dron activo (lower):** $U_i \geq \frac{1}{m-1}\sum_{j \neq 1}\sum_k X_{ijk}$
4. **CS primero:** $X_{i,1,1} = 1$
5. **CS exactamente dos veces:** $\sum_k X_{i,1,k} = 2$
6. **Nada después de CS (Big-M, M=m):** $(1-X_{i,1,k})\cdot m \geq \sum_{j \neq 1}\sum_{k_2=k+1}^{|K|} X_{ijk_2}$, $k \neq 1$
7. **Un punto por posición:** $\sum_{j \neq 1} X_{ijk} \leq 1$
8. **Cada punto visitado una vez:** $\sum_i\sum_k X_{ijk} = 1$, $j \neq 1$
9. **Extremos consecutivos (≤):** $X_{ij_1k} \leq \sum_{j_2 \neq 1}(X_{ij_2,k-1}+X_{ij_2,k+1})b_{j_1j_2}$, $j_1 \neq 1$, $k \notin \{1,|K|\}$
10. **Sin saltos:** $\sum_{j \in J} X_{ijk} \leq \sum_{j \in J} X_{ij,k-1}$, $k \neq 1$

### Instancia Valdebueyes3

- $n=10$, $|\text{barridos}|=122$, $m=245$, $(x_{cs}, y_{cs})=(-200, 2500)$

---

## Pending clues — constraints potentially missing in current formulation

These clues were given to the user (Juan Camilo) during a review of his formulation.
The user requested clues only, not full constraints. He is working through them one by one.

### Clue 1 — Sequencing without gaps (route contiguity) — RESOLVED

User added: $\sum_{j \in J} X_{ijk} \leq \sum_{j \in J} X_{ij,k-1}$ for all $i$ and $k \neq 1$.
Sum is over full $J$ (CS included) on both sides — needed at $k=2$ since CS at $k-1=1$
provides the count of 1 that allows a sweep at $k=2$.

### Clue 2 — Start of route activation — RESOLVED (subsumed by Clue 1)

Once Clue 1 is in place, "disconnected" assignments after $k=1$ are impossible:
any sweep at position $k$ requires a continuous chain back to $k=1$ (which holds CS).
No additional constraint needed.

### Clue 3 — Fleet limit (NOT missing)

No explicit constraint $\sum_i U_i \leq n$ is needed. The cardinality of $I$
already bounds the sum implicitly. This was confirmed earlier in the conversation.

---

## Status notes

- **Most critical missing piece:** Clue 1. If solved correctly, Clue 2 may
  become unnecessary.
- **User preference:** he wants to derive each constraint himself; provide
  hints and verify his proposals, do not write the final form.
