# Prompt: Crear póster académico

**Título:** Ranking de Recomendaciones Médicas de LLMs
**Autor:** Juan Camilo España — CAE, Universidad de Oviedo

---

Crea un póster académico de una sola diapositva  con la siguiente información estructurada, sin cambiar los datos en este prompt:

## 1. Datos
- 3 datasets (10 atributos numéricos, mismos que cuantificación)
- ranking_E1: 418 recomendaciones, 200 Lotes × 5 recoemdnaciones por lote — entrenamiento/Eval
- ranking_E2: 255 recomendaciones, 100 lotes × 5 recomendaciones por lote — entrenamiento/Eval	
- dataset_E3: 313 recomendaciones, sin etiquetas — producción
- Calificación por experto: 0–10 por recomendación

## 2. Proceso
- 3 modelos entrenados sobre E1+E2 combinados (1500 filas)
- Evaluación: C-index (pares bien ordenados) y NDCG (calidad top posiciones)
- Validación cruzada: GroupKFold 3 folds (grupos = lote, nunca divididos)

## 3. Resultados

| Modelo | C-index train | NDCG train | C-index CV | NDCG CV |
|---|---|---|---|---|
| linearRank | 0.507 | 0.828 | **0.515** | **0.837** |
| XGBRanker pairwise | 0.821 | 0.948 | 0.500 | 0.829 |
| XGBRanker ndcg | 0.740 | 0.947 | 0.496 | 0.824 |

Ganador: **linearRank** — Mejor desempeño en evaluación en ambas méticas y menor sobreajuste.

- Ranking E3: 313 recomendaciones ordenadas, scores entre −3.27 y 3.91
- Top-1: recomendación #14 (score 3.91)

---


**Estilo del póster:** Tipo Poster infográfico vertical, estilo minimalista, pocos colores, poco texto, académico, conciso, en español