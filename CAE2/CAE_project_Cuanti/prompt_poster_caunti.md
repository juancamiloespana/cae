# Prompt: Crear póster académico

**Título:** Cuantificación de Alucinaciones en Recomendaciones Médicas de LLMs
**Autor:** Juan Camilo España — CAE, Universidad de Oviedo

---

Crea un póster académico de una sola diapositva  con la siguiente información estructurada, sin cambiar los datos en este prompt:

## 1. Datos
- 3 datasets sintéticos (10 atributos numéricos)
- E1: 418 muestras, prevalencia 15% — entrenamiento
- E2: 255 muestras, prevalencia 25% — evaluación (LLM diferente)
- E3: 313 muestras, prevalencia desconocida — producción

## 2. Proceso
- Clasificador base: Random Forest entrenado en E1
- 4 cuantificadores entrenados y evaluados (E1,E2): CC, AC, PAC, DFX-ganador 0.L1=0269 y L2=0.0007
- Afinamiento del DFX con Optuna: 200 intentos
	L1= 0.0015 despues de afinar en E2
- Robustez: 200 bags sobre E2: L1= 0.11
- Modelo final: reentrenado con E1+E2, aplicado sobre E3

## 3. Resultados
|
Ganador:

| **DFX afinado** (n_bins=28, L1),  L1 en E2**0.0015**, L1 bags: 0,11 

- Prevalencia estimada en E3: **29.9%** (real: 35%, L1=0.05)

---

**Estilo del póster:** Tipo Poster infográfico vertical, estilo minimalista, pocos colores, poco texto, académico, conciso, en español