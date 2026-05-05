# -*- coding: utf-8 -*-
"""
Sesión 2 : Ranking
Actividad 1 y 2
"""

# Datos de sushi
# Mira los ficheros de origen y las variables que genera 
from readSushi import readSushi
[Xsushi,Ysushi]=readSushi()


# XGBRanker en sklearn
# Para incluir XGBRanker en sklearn hacemos un wrapper.
#   La principal diferencia es el método fit, que tiene como parámetros: X, Y, qid (también podría ser group)
# https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRanker
# Install: https://xgboost.readthedocs.io/en/latest/install.html

import numpy as np
from xgboost import XGBRanker
from sklearn.base import BaseEstimator
class SKWrapperXGBRanker(BaseEstimator):
    """
    Wrapper of a XGBRanker into sklearn enviroment with [value,batch] values at Y
    """
    def __init__(self,xgbranker):
        """
        Param:
            xgbranker : a XGBRanker object
        """
        self.xgbranker=xgbranker
        
    def getXGBRanker(self):
        return self.xgbranker
        
    def fit(self,X,Y):
        """
        Transforms Y from a list of [value,batch] to use in XGBRanker.fit and call it
        Reorder the examples to get an ordered qid list
        """        
        Y=np.array(Y)
        X=np.array(X)
        
        # Get the arrays
        xgY=Y[:,0]
        qid=Y[:,1]
        
        # Reorder
        order=np.argsort(qid)
        X=X[order]
        xgY=xgY[order]
        qid=qid[order]
        
        return self.xgbranker.fit(X,xgY,qid=qid)
    
    def predict(self,X):
        return self.xgbranker.predict(X)

# Actividad 1
"""
Enunciado Actividad 1:
Para el conjunto de datos de sushi (Xsushi, Ysushi), realiza una experimentación 
en la que se estimen las métricas C-index y NDCG para los siguientes modelos: 
    un sistema de ranking lineal
    XGBRanker con objective=‘rank:pairwise’
    XGBRanker con objective=‘rank:ndcg’.
Asimismo, calcula el valor de estas métricas en el conjunto de reescritura.
Almacena los modelos y los valores de las métricas para cada sistema
"""

#<TODO BEGIN Actividad 1>
"""
Procedimiento Actividad 1

En sklearn existe la métrica: ndcg_score.
¿Porqué no se puede utiliziar directamente? (Hay 2 motivos)
Crea una medida que se pueda utilizar en este caso

Crea un par de listas:
    RankersObj  : objetos ranker
    RankersName : nombres de los objetos anteriores
    
Crea una lista vacía para almacenar los modelos y las métricas.
    
Itera por cada uno de estos ranker realizando para todos ellos las acciones pedidas
"""
from copy import deepcopy
# Utiliza deepcopy(ranker) para guardar el modelo

from Rank import linearRank,multiBatch,multiBatchCIndex
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer,ndcg_score
from sklearn.model_selection import GroupKFold
                                        
RankersObj =[ linearRank(),
             SKWrapperXGBRanker(XGBRanker(objective='rank:pairwise')),
             SKWrapperXGBRanker(XGBRanker(objective='rank:ndcg'))]
RankersName=['linearRank' ,
             'WXGBRanker_pairwise',
             'WXGBRanker_ndcg']

RankersModelMetrics=[]

# Métrica NDCG
multiBatchNDCG=multiBatch(lambda Y,P:ndcg_score([Y],[P]),ponderation='pairs')

# Los grupos del CrossValidation son los lotes
groups=[]
for [value,idLote] in Ysushi:
    groups.append(idLote)

# Scores a calacular en el CrossValidation
scores={'C-index':make_scorer(multiBatchCIndex),
        'NDCG'   :make_scorer(multiBatchNDCG)}

for i in range(len(RankersObj)):
    ranker=RankersObj[i]
    rName =RankersName[i]
    
    # Crea el modelo
    ranker.fit(Xsushi,Ysushi)
    P=ranker.predict(Xsushi)
    CIndex=multiBatchCIndex(Ysushi,P)
    ndcg  =multiBatchNDCG(Ysushi,P)
    print('{} Overwrite: C-index={:6.4f} NDCG={:6.4f}'.format(rName,CIndex,ndcg))
    
    # Guárdalo
    ModelMetrics=[deepcopy(ranker)] # ¿Porqué deepcopy? cross_validate modificará ranker

    CVscores=cross_validate(ranker,Xsushi,Ysushi,scoring=scores,
                            groups=groups,cv=GroupKFold(n_splits=3,shuffle=True,random_state=1))
    print('{}: Cross Validation'.format(rName))
    for key in scores.keys():
        mValue=np.mean(CVscores['test_{}'.format(key)])
        print('  {}={:6.4f}'.format(key,mValue))
        ModelMetrics.append(mValue)
    
    RankersModelMetrics.append(ModelMetrics)

#<TODO END Actividad 1>

groups
np.array(Xsushi).shape
np.array(Ysushi).shape
Xsushi.shape

from readSushi import getObjetoSushi

# Objetos según se leen del CSV
s1Ori=['7','tamago','1','1','9','2.36807095343681','1.86622320768662','1.03246753246753','0.84']
s2Ori=['8','toro','1','0','1','0.551854655563967','2.05753217259652','4.48545454545455','0.8']

# Objetos con valores numéricos
[ids1,s1]=getObjeto(s1Ori)
[ids2,s2]=getObjeto(s2Ori)

"""
Enunciado actividad 2
Utiliza el mejor modelo para evaluar estos 2 sushis.
Indica qué sushi es el mejor
"""

#<TODO BEGIN Actividad 2>

# Calcular el mejor modelo.
# Comprobar si hay un modelo que es el mejor para todas las métricas

RankersModelMetrics=np.array(RankersModelMetrics)
mejores=[]
scoresKeys=list(scores.keys())
for i in range(len(scoresKeys)):
    im=np.argmax(RankersModelMetrics[:,i+1])
    mejores.append(im)
    print('Mejor para métrica {:7} : {}'.format(scoresKeys[i],RankersName[im]))

if min(mejores)==max(mejores): # Todos son el mismo
    print('Mejor modelo para todas métricas: {}'.format(RankersName[mejores[0]]))
    ranker=RankersModelMetrics[mejores[0]][0]
else:
    raise('Por implementar discrepancia de métricas')


# 2.2 : Evalua ambos sushis, imprime sus evaluaciones
ev1=ranker.predict([s1])[0]
ev2=ranker.predict([s2])[0]
print('Sushi {} evaluado con {:+6.4f}'.format(s1Ori[0],ev1))
print('Sushi {} evaluado con {:+6.4f}'.format(s2Ori[0],ev2))

# 2.3 : Implementa el código que indique cual es el mejor
if ev1>ev2:
    mejor=s1Ori[1]
    peor= s2Ori[1]
else:
    mejor=s2Ori[1]
    peor= s1Ori[1]
print('Sushi {} mejor que sushi {}'.format(mejor,peor))

#<END Actividad 2>






