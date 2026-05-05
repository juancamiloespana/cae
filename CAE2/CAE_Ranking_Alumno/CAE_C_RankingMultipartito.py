# -*- coding: utf-8 -*-
"""
Sesión 2 : Ranking
Bloque C : Aprendizaje de ranking multipartito de un solo lote
"""

# 
# Estamos en la situación que el valor de ranking (la categoría) tiene
#diferentes valores numéricos, puden ser valores discretos o en coma flotante.
# En esta práctica se trabajará solo con un lote. 
# El objetivo es el ordenar los ejemplos del test de manera que los ejemplos 
#con valores mayores estén antes que los ejemplos con valores menores.
# La métrica CIndex (Concordance index) calcula la proporción de pares
#correctamente ordenados


# Leer qsar_aquatic_toxicity.csv

# Leer datos de datasets/qsar_aquatic_toxicity.csv
#https://archive.ics.uci.edu/ml/datasets/QSAR+aquatic+toxicity
# La última columna es la categoría (calidad del agua), es un valor en coma flotante
#pero nos interesa solo el valor entero, así que se aplicará la función round
# El resto de columnas (toas menos la última) será los atributos
# Crear valiables X,Y donde se guarden los datos de este conjunto
# Se tomarán solo los 100 primeros ejemplos (por razones de eficiencia)

import csv
X=[]
Y=[]
with open('datasets/qsar_aquatic_toxicity.csv') as csvfile:
    Reader=csv.reader(csvfile,delimiter=';',quoting=csv.QUOTE_NONNUMERIC)
    for row in Reader:
        X.append(row[:len(row)-1])
        Y.append(round(row[len(row)-1]))

X=X[:100]
Y=Y[:100]



# Estimación de CIndex
# Realizar una validación cruzada con 3 folds del sistema linearRank con el 
#conjuto de datos anterior. Estimar CIndex

from CAE_project_ranking.Rank import linearRank,CIndex
from sklearn.model_selection import cross_validate
from sklearn.metrics import make_scorer

Ranker=linearRank(verbose=1)
cv=cross_validate(Ranker,X,Y,scoring=make_scorer(CIndex),cv=3)
print('CIndex={:6.4f}'.format(cv['test_score'].mean()))

# Ejercicio 1
# Los valores de la Y son enteros en [0;10], pero solo interesa la calidad del
#agua según los siguientes criterios:
# Mala    : [0; 4]
# Regular : [5; 7]
# Buena   : [8:10]
# Modifica los valores de la Y de manera que las aguas con el mismo criterio tengan
#un mismo valor y sea acorde a Buena>~Regular>~Mala
# Repite el experimento anterior y calcula la estimación del CIndex para este caso
# El CIndex, ¿Ha mejorado o empeorado?

#<TODO BEGIN Ejerccio 1>

# Generando Y3 donde Mala->0, Regular->1, Buena->2
Y3=[]
for v in Y:
    if v <=4:
        c=0
    elif v<=7:
        c=1
    else:
        c=2
    Y3.append(c)

# Experimentación
cv=cross_validate(Ranker,X,Y3,scoring=make_scorer(CIndex),cv=3)
print('Y3: CIndex={:6.4f}'.format(cv['test_score'].mean()))

#<TODO END Ejerccio 1>

cv['test_score']

