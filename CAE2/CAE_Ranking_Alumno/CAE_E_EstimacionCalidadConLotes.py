# -*- coding: utf-8 -*-
"""
Sesión 2 : Ranking
Bloque E : Estimación de la medida de calidad con varios lotes
"""

# 
# Como se indicó en el bloque A, los conjuntos de ejemplos de ranking están agrupados
#por lotes. Para estimar una medida de calidad se realizará una validación cruzada
#pero agrupando por lote, no por ejemplo.


# Ejemplo restaurantes

# Datos del bloque A
# Restaurantes
R1=[9.4,  5.0]
R2=[0.5, -1]
R3=[3.5,  0]
R4=[7.5,  2.3]

X=[R2    ,R1    ,R2    ,R4    ,R3    ,R1    ,R2    ,R3    ,R4    ,R1]
Y=[[2,1] ,[1,1] ,[3,2] ,[2,2] ,[2,2] ,[1,2] ,[4,3] ,[3,3] ,[2,3] ,[1,3]]


# Estimación del error con lotes

from CAE_project_ranking.Rank import linearRank
from CAE_project_ranking.Rank import multiBatchCIndex
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer
from sklearn.model_selection import GroupKFold

ranker=linearRank()

[m[1] for m in Y]
# Los grupos son los lotes
groups=[]
for [value,idLote] in Y:
    groups.append(idLote)

# Se ha de utilizar una validación cruzada donde se indica en groups los lotes
#y se utiliza como cv un objeto de la clase GroupKFold
CVscores=cross_validate(ranker,X,Y,scoring=make_scorer(multiBatchCIndex),
                        groups=groups,cv=GroupKFold(n_splits=3)) # No puede haber más folds que lotes

## grupos son lotes qué son grupos? identidad

print('CIndex (proporción de pares correctamente ordenados en cada lote): {:6.4f}'
       .format(CVscores['test_score'].mean()))

# Ejercicio 1
# Haz de crítico y añade unas nuevas preferencias sobre restaurantes.
# Escribe las preferencias como R1 >~ R2, o R2 <~ R4
# Codifica estas preferencias y añádelas a X e Y
# Estima el error con el máximo número de folds
#<TODO BEGIN Ejercicio 1>

# Preferencias como crítico
# R2 <~ R4
# R3 >~ R4 >~ R1

# Codificación de las preferencias en los lotes 4 y 5
XN=[ R2  , R4  , R3   ,R4  , R1]
YN=[[2,4],[3,4],[3,5],[2,5],[1,5]] # Se empieza en el lote 4, que el último fue el 3

# Se concatenan los datos
XAll=X+XN
YAll=Y+YN

# Los grupos son los lotes
groups=[]
for [value,idLote] in YAll:
    groups.append(idLote)

# Estimar la medida de calidad mediante cross validation
CVscores=cross_validate(ranker,XAll,YAll,scoring=make_scorer(multiBatchCIndex),
                        groups=groups,cv=GroupKFold(n_splits=5))# Hay 5 grupos, así que max de folds = 5

# Imprimir
print('Datos nuevos: CIndex (proporción de pares correctamente ordenados en cada lote): {:6.4f}'
       .format(CVscores['test_score'].mean()))

#<TODO END Ejercicio 1>


