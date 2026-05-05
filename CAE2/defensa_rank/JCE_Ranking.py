# -*- coding: utf-8 -*-
"""
Análisis de los resultados de los modelos de ranking en el conjunto de datos de recomendaciones médicas de LLM

Las recomendaciones médicas caracterizadas con los atributos de dataset_E1.csv y dataset E2 fueron evaldas de la siguente manera:

Recomendaciones: E1: 418, mismas que en Dataset de cauntificación
Recomendaciones: E2: 255, diferentes a las de E1, mismas que en Dataset de cuantificación

Lotes: 200 para E1, 100 para E2. Que son el número de expertos que hacen las evaluaciones, cada experto genera un lote diferente.

Tamaño de lote: 5, cada experto evalúa 5 recomendaciones diferentes, por lo que cada lote tiene 5 recomendaciones.
Se quieren utilizar estos datos para entrenar los modelos y utilizarlos para definir las preferencias para dataset_E3.
"""

# =============================================================================
# IMPORTS
# =============================================================================

import numpy as np
import pandas as pd
from xgboost import XGBRanker
from sklearn.base import BaseEstimator
from copy import deepcopy

from Rank import linearRank, multiBatch, multiBatchCIndex, multiBatchNDCG
from Rank import SKWrapperXGBRanker
from sklearn.model_selection import cross_validate, GroupKFold
from sklearn.metrics import make_scorer, ndcg_score






class CombiRanking(BaseEstimator):
    """
    Combina sistemas de ranking prediciendo la media del ranking
    """
    
    def __init__(self,RList):
        """
        Params:
            RList : Lista de cuantificadores (objetos de quantificationlib)
        """
        self.RList=RList
        self.classes_=None
        
    def fit(self,X,Y):
        """
        Entrena todos los sistemas de RList
        """        
        # A) Entrena(fit) los sistemas de self.RList
    
        for i, R in enumerate(self.RList):

            self.RList[i]=R.fit(X, Y)
			

            
        return self
    
    def predict(self,X):
        """
        Predice la prevalencia como la media de las prevalencias de cada sistema
        """
        ranks=[]
        for R in self.RList:
            # B) En rank se almacena el ranking para el sistema R
            rank=R.predict(X)
            ranks.append(rank)
        avgrank=np.mean(ranks,axis=0)
        
        return avgrank
        


# =============================================================================
# CARGA DE DATOS
# =============================================================================

df1_Ranking_E1 = pd.read_csv('datasets/ranking_E1.csv')
df2_Ranking_E2 = pd.read_csv('datasets/ranking_E2.csv')
X_E3 = pd.read_csv('datasets/dataset_E3.csv').drop(columns=['y_alucinacion']).values

YE1 = df1_Ranking_E1.values[:, 0:2]
X_E1 = df1_Ranking_E1.values[:, 2:]
YE2 = df2_Ranking_E2.values[:, 0:2]
X_E2 = df2_Ranking_E2.values[:, 2:]

# Une E1 y E2 en un único conjunto de entrenamiento
Y_combined = np.concatenate((YE1, YE2), axis=0)
X_combined = np.concatenate((X_E1, X_E2), axis=0)


# =============================================================================
# CONFIGURACIÓN DE MODELOS Y MÉTRICAS
# =============================================================================
# Indicadores definidos en Rank.py: multiBatchCIndex, multiBatchNDCG




RankersObj = [
    linearRank(),
    SKWrapperXGBRanker(XGBRanker(objective='rank:pairwise')),
    SKWrapperXGBRanker(XGBRanker(objective='rank:ndcg'))

]


list_combi=RankersObj[0:2]


combi=CombiRanking(list_combi)
RankersObj.append(combi)

combi.fit(X_combined, Y_combined)

# combi
# combi.predict(X_combined)



RankersName = [
    'linearRank',
    'WXGBRanker_pairwise',
    'WXGBRanker_ndcg',
    'combin_ranker'
]

RankersModelMetrics = []
TrainMetrics = []  # guarda (CIndex, NDCG) en entrenamiento para las figuras

# Grupos para GroupKFold: columna 'lote' de Y_combined (índice 1)
groups = [i[1] for i in Y_combined]

scores = {
    'C-index': make_scorer(multiBatchCIndex),
    'NDCG':    make_scorer(multiBatchNDCG),
}


# =============================================================================
# ENTRENAMIENTO Y VALIDACIÓN CRUZADA
# =============================================================================

for i in range(len(RankersObj)):
    ranker = RankersObj[i]
    rName  = RankersName[i]

    # Entrena sobre el conjunto completo y mide sobreajuste
    ranker.fit(X_combined, Y_combined)
    P      = ranker.predict(X_combined)
    CIndex = multiBatchCIndex(Y_combined, P)
    ndcg   = multiBatchNDCG(Y_combined, P)
    print('{} Overwrite: C-index={:6.4f} NDCG={:6.4f}'.format(rName, CIndex, ndcg))
    TrainMetrics.append((CIndex, ndcg))

    # deepcopy necesario porque cross_validate modifica el objeto ranker internamente
    ModelMetrics = [deepcopy(ranker)]

    CVscores = cross_validate(ranker, X_combined, Y_combined, scoring=scores,
                              groups=groups, cv=GroupKFold(n_splits=3, shuffle=True, random_state=1))
    print('{}: Cross Validation'.format(rName))
    for key in scores.keys():
        mValue = np.mean(CVscores['test_{}'.format(key)])
        print('  {}={:6.4f}'.format(key, mValue))
        ModelMetrics.append(mValue)

    RankersModelMetrics.append(ModelMetrics)


# =============================================================================
# SELECCIÓN DEL MEJOR MODELO
# =============================================================================

RankersModelMetrics = np.array(RankersModelMetrics)
mejores = []
scoresKeys = list(scores.keys())

for i in range(len(scoresKeys)):
    im = np.argmax(RankersModelMetrics[:, i + 1])
    mejores.append(im)
    print('Mejor para métrica {:7} : {}'.format(scoresKeys[i], RankersName[im]))

if min(mejores) == max(mejores):  # Todas las métricas coinciden en el mismo modelo
    print('Mejor modelo para todas métricas: {}'.format(RankersName[mejores[0]]))
    ranker = RankersModelMetrics[mejores[0]][0]
else:
    raise('Por implementar discrepancia de métricas')


# =============================================================================
# PREDICCIÓN SOBRE E3 Y CONSTRUCCIÓN DEL RANKING FINAL
# =============================================================================

scores_E3 = ranker.predict(X_E3)

DF_E3 = pd.DataFrame(X_E3, columns=df2_Ranking_E2.columns[2:])
DF_E3.insert(0, 'score_predicho', scores_E3)
DF_E3.reset_index(inplace=True, drop=False)
DF_E3.rename(columns={'index': 'id'}, inplace=True)
DF_E3 = DF_E3.sort_values(by='score_predicho', ascending=False)
DF_E3.reset_index(inplace=True, drop=True)
DF_E3.insert(1, 'rank_predicho', DF_E3.index + 1)


# =============================================================================
# FIGURAS PARA EL INFORME
# =============================================================================

import matplotlib.pyplot as plt
import os
os.makedirs('figures', exist_ok=True)

names_short = ['linearRank', 'XGB pairwise', 'XGB ndcg', 'combi']

# --- FIGURA 1: histograma de calificaciones en E1 y E2 ---
fig, axes = plt.subplots(1, 2, figsize=(9, 3.5), sharey=True)
df1_Ranking_E1['calificacion'].plot.hist(ax=axes[0], bins=11, color='steelblue', edgecolor='white')
axes[0].set_title('E1 (200 lotes)'); axes[0].set_xlabel('Calificación')
df2_Ranking_E2['calificacion'].plot.hist(ax=axes[1], bins=11, color='tomato', edgecolor='white')
axes[1].set_title('E2 (100 lotes)'); axes[1].set_xlabel('Calificación')
plt.tight_layout()
plt.savefig('figures/hist_calificaciones.pdf')
plt.show()

# --- FIGURA 2: barras C-index y NDCG en CV (y entrenamiento) ---
ci_cv = [float(RankersModelMetrics[i, 1]) for i in range(len(RankersName))]
nd_cv = [float(RankersModelMetrics[i, 2]) for i in range(len(RankersName))]
x = np.arange(len(RankersName)); w = 0.35
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(x - w/2, ci_cv, w, label='C-index (CV)', color='steelblue')
ax.bar(x + w/2, nd_cv, w, label='NDCG (CV)',    color='tomato')
ax.set_xticks(x); ax.set_xticklabels(names_short)
ax.set_ylim(0, 1); ax.set_ylabel('Métrica'); ax.legend()
ax.set_title('Desempeño en validación cruzada (3 folds)')
plt.tight_layout()
plt.savefig('figures/cv_metricas.pdf')
plt.show()

# --- FIGURA 3: histograma de scores predichos en E3 ---
plt.figure(figsize=(6, 3.5))
plt.hist(scores_E3, bins=30, color='steelblue', edgecolor='white')
plt.xlabel('Score predicho'); plt.ylabel('Frecuencia')
plt.title('Distribución de scores en E3')
plt.tight_layout()
plt.savefig('figures/scores_E3.pdf')
plt.show()

DF_E3
