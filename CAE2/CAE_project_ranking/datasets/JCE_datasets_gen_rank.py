import random
import pandas as pd


### leer datos de atributos de recomendaciones de LLM

dataset_E1 = pd.read_csv('dataset_E1.csv').drop(columns=['y_alucinacion']) 
dataset_E2 = pd.read_csv('dataset_E2.csv').drop(columns=['y_alucinacion'])
dataset_E3 = pd.read_csv('dataset_E3.csv').drop(columns=['y_alucinacion'])
	  


############## rankings de recomendaciones LLM ####

def genRanking(RG, df, n_lotes, tam_lote=10):
    """
    Genera lotes de ranking sobre las filas de un DataFrame.

    Parámetros:
        RG       : objeto random.Random()
        df       : DataFrame con las recomendaciones (cada fila es una recomendación)
        n_lotes  : número de lotes a generar
        tam_lote : número de filas por lote (sin repetición dentro del lote)

    Retorna:
        DataFrame (n_lotes * tam_lote, 2 + n_features) con columnas:
            ['calificacion', 'lote', ...columnas de df]
    """
    indices = list(df.index)
    rows = []
    for lote in range(n_lotes):
        for fila in RG.sample(indices, tam_lote):
            rows.append([RG.randint(0, 10), lote] + list(df.loc[fila].values))
    return pd.DataFrame(rows, columns=['calificacion', 'lote'] + list(df.columns))


RG = random.Random()
RG.seed(42)

ranking_E1 = genRanking(RG, dataset_E1, n_lotes=200, tam_lote=5)
ranking_E2 = genRanking(RG, dataset_E2, n_lotes=100, tam_lote=5)


ranking_E1.to_csv('ranking_E1.csv', index=False)
ranking_E2.to_csv('ranking_E2.csv', index=False)




