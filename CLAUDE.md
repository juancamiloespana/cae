# CLAUDE.md — CAE (repo root)

## Structure

```
CAE_lin/
├── CAE1_lin/   ← active working folder — all CAE1 detail here
└── CAE2/       ← quantification and ranking projects (Python)
```

**All CAE1 detail** (Java setup, Opt4J, plugins, experiments, sync) is in:
`CAE1_lin/CLAUDE.md`

---

## CAE2 — Proyecto Cuantificación

Estimar prevalencia de alucinaciones en recomendaciones médicas de LLMs. Tres datasets sintéticos: E1=entrenamiento (prevalencia 0.15), E2=test distinto LLM (0.25), E3=producción sin etiquetas (0.35).

- **Dataset** (`JCE_datasets_gen`): 10 features LLM, 20% ruido cruzado, `y_alucinacion` como primera columna
- **Cuantificadores** (`JCE_Cuantificacion.py`): `CC`, `AC`, `PAC`, `DFX` con base `RandomForestClassifier(n_estimators=100)`
- **DFX afinado con Optuna**: `n_bins` ∈ [10,200], `distance` ∈ `['L1','L2','HD']` — `'topsoe'` no soportado
- Importar `dataSetFromQBags` desde `QUtils`, no desde `quantificationlib.utils.utilities`

---

## CAE2 — Proyecto Ranking

Ranking de recomendaciones LLM usando lotes de preferencias con calificaciones.

- **Generador** (`JCE_datasets_gen_rank`): `genRanking(RG, df, n_lotes, tam_lote=10)`
- Retorna DataFrame con columnas `['calificacion', 'lote', ...features]`; `calificacion` entero 0–10
- E1: 200 lotes × 5 filas · E2: 100 lotes × 5 filas
