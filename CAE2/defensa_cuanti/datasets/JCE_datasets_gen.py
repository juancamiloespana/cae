import random
import pandas as pd

# Features de texto generado por LLM para detección de alucinaciones
FEATURE_NAMES = [
    'n_words',   # Número de palabras en el texto
    'n_refs',    # Número de referencias o citas mencionadas
    'lex_div',   # Diversidad léxica: proporción de palabras únicas sobre total
    'hedge_r',   # Tasa de expresiones de incertidumbre: "podría", "quizás"
    'spec_sc',   # Puntuación de especificidad: qué tan concretos son los detalles
    'sent_pol',  # Polaridad del sentimiento promedio de las oraciones
    'consist',   # Consistencia interna: coherencia entre afirmaciones del texto
    'src_dens',  # Densidad de fuentes: menciones de autores, fechas, publicaciones
    'num_dens',  # Densidad numérica: cantidad de cifras o estadísticas por oración
    'verb_ten',  # Mezcla de tiempos verbales: varianza en el uso de tiempos verbales
]

# Distribuciones por clase: medias simétricas, dt similares para que la escala no domine
#                   n_words  n_refs  lex_div  hedge_r  spec_sc  sent_pol  consist  src_dens  num_dens  verb_ten
MEDIA_0 = [-1.0,   -0.8,     0.5,   -0.5,    1.0,    -1.2,     0.3,    -0.7,     0.8,     -0.3]
MEDIA_1 = [ 1.0,    0.8,    -0.5,    0.5,   -1.0,     1.2,    -0.3,     0.7,    -0.8,      0.3]
DT_0    = [ 0.8,    0.9,     0.7,    1.0,    0.8,     0.9,     1.0,     0.7,     0.8,      0.9]
DT_1    = [ 0.9,    0.7,     1.0,    0.8,    0.9,     0.7,     0.8,     1.0,     0.9,      0.8]


def genToy(RG, nEjemplos, prevalencia,
           media0=MEDIA_0, media1=MEDIA_1,
           dt0=DT_0,       dt1=DT_1,
           ruido=0.20):
    """
    Genera un dataset de nEjemplos con 10 features de texto LLM.
    Clase 0 = no alucinación, Clase 1 = alucinación.

    Parámetros:
        RG          : objeto random.Random()
        nEjemplos   : número de ejemplos a generar
        prevalencia : proporción de ejemplos de clase 1 (alucinación)
        media0, dt0 : media y dt de cada feature para clase 0
        media1, dt1 : media y dt de cada feature para clase 1
        ruido       : proporción de etiquetas invertidas (0.20 = 20% de ruido)

    Retorna:
        DataFrame nEjemplos x 11: columna 'y_alucinacion' al inicio, seguida de los 10 features
    """
    ePos = int(nEjemplos * prevalencia)
    eNeg = nEjemplos - ePos

    rows, Y = [], []
    for _ in range(eNeg):
        dist = (media1, dt1) if RG.random() < ruido else (media0, dt0)
        rows.append([RG.normalvariate(dist[0][i], dist[1][i]) for i in range(10)])
        Y.append(0)
    for _ in range(ePos):
        dist = (media0, dt0) if RG.random() < ruido else (media1, dt1)
        rows.append([RG.normalvariate(dist[0][i], dist[1][i]) for i in range(10)])
        Y.append(1)

    df = pd.DataFrame(rows, columns=FEATURE_NAMES)
    df.insert(0, 'y_alucinacion', Y)
    return df


preE1 = 0.15  # Prevalencia de Evaluación 1 de modelos con etiquetas asignadas manualmente por médicos
preE2 = 0.25  # Prevalencia de Evaluación 2 de modelos con etiquetas asignadas manualmente por médicos con una version diferente de LLM
preE3 = 0.35  ## prevalencia de set de evaluación 3 sin etiquetas asignadas (Producción)

RG = random.Random()
RG.seed(1)

dataset_E1 = genToy(RG, 418, prevalencia=preE1)
dataset_E2 = genToy(RG, 255, prevalencia=preE2)  ## el cambio en la distribuc
dataset_E3 = genToy(RG, 313, prevalencia=preE3)  # Solo features, sin etiquetas (Producción)


dataset_E1.to_csv('dataset_E1.csv', index=False)
dataset_E2.to_csv('dataset_E2.csv', index=False)
dataset_E3.to_csv('dataset_E3.csv', index=False)