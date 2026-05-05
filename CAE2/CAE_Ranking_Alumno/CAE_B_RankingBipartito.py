# -*- coding: utf-8 -*-
"""
Sesión 2 : Ranking
Bloque B : Aprendizaje a partir de ranking bipartito en un solo lote
"""

# 
# El objetivo del aprendizaje automático de rankings es crear un modelo que dado
#un ejemplo le otorgue un valor numérico de manera que si este valor es mayor
#que el dado a otro ejemplo indica que se prefiere el primero al segundo.

# Estamos en la situación que el valor de ranking (la categoría) solo tiene dos
#valores se llamarán positivo y negativo. 
# En esta práctica se trabajará solo con un lote. 
# El objetivo es el ordenar los ejemplos del test de manera que los positivos
#estén antes que los negativos.

# La clase linearRank realiza el proceso de aprendizaje de un modelo lineal

# conjunto de datos aleatorio

import random
import numpy as np
from CAE_project_ranking.Rank import linearRank
from sklearn.metrics import roc_auc_score
from sklearn.metrics import RocCurveDisplay


def genXY(RG,w,nEje,ruido=0):
    X=[None]*nEje
    Y=[None]*nEje
    at=len(w)
    for e in range(nEje):
        x=list(RG.gauss(0,1) for i in range(at))
        X[e]=x
        
        vRuido=RG.uniform(1,2)*RG.choice([-1,+1])*ruido # Uniform distribution in (-2*ruido;-1] U [+1;+2*ruido)
        vx=np.dot(x,w)# Producto escalar
        v=vx+vRuido
        # Valor 1 si positivo, 0 si negativo
        if v>0:
            Y[e]=1
        else:
            Y[e]=0
    return [X,Y]

nAtt=10     # Atributos

RG=random.Random() # Generador de aletoriedad
RG.seed(1)
w=list(RG.gauss(0,1) for i in range(nAtt)) # Pesos de la función lineal que dará las evaluaciones

nEjeTr=100  # Ejemplos de entrenamiento
nEjeTe=100  # Ejemplos de test
ruido=1     # Ruido. 0 no hay ruido, cuanto mayor, más ruido

[XTr,YTr]=genXY(RG,w,nEjeTr,ruido)
[XTe,YTe]=genXY(RG,w,nEjeTe,ruido)



print('Generado entranamiento({} ejemplos) test({} ejemplos)'.format(len(XTr),len(XTe)))

    
# Realizar un entrenamiento y obtener una evaluación del test

# Clasificador, lineal y sin término independiente. 
# Genera como salida la evaluación de la función lineal  
lRank=linearRank()

print('Generando modelos a partir del train y evaluando el test')
Model=lRank.fit(XTr,YTr)
Eval=Model.predict(XTe)

# Evaluar la calidad de los modelos de ranking

# La calidad de los modelos de ranking bipartitos se mide usando AUC
#La medida roc_auc_score realiza este cálculo

print('Evaluando la calidad de los modelos de ranking')
AUC=roc_auc_score(YTe,Eval)
print('AUC={:6.4f}'.format(AUC))
RocCurveDisplay.from_predictions(YTe,Eval)

#EL auc dice que numero de pares ordenó bine

    
# Ejercicio 1
# Variar el ruido desde 0 hasta 10. Para cada nivel de ruido generar un conjunto
#de datos con ese ruido. Crear un modelo de ranking con el entrenamiento y
#calcular el AUC del test. Imprimir el AUC.
# EXTRA: Hacer una gráfica en la que vea como varía el AUC en función del ruido

AUCs=[]# Se almacenarán los AUC en esta lista
ruidos=list(range(10+1)) # Ruidos de 0 a 10
#<TODO BEGIN Ejerccio 1>

# Cálculo del AUC por cada nivel de ruido
for ruido in ruidos:
  
    # Generación del conjunto de ejemplos
    [XTr,YTr]=genXY(RG,w,nEjeTr,ruido)
    [XTe,YTe]=genXY(RG,w,nEjeTe,ruido)
    
    # Aprendizaje / evaluación
    Model=lRank.fit(XTr,YTr)
    Eval=Model.predict(XTe)
    
    # Cálculo del AUC
    AUC=roc_auc_score(YTe,Eval)
    
    # Almnacenar el AUC en AUCs
    AUCs.append(AUC)
    
    # Imprimir
    print('ruido={:2} AUC={:6.4f}'.format(ruido,AUC))

#<TODO END Ejerccio 1>
# Gráfica de AUC en función del ruido
import matplotlib.pyplot as plt
plt.figure()
plt.title('Ejercicio 1 (Extra). AUC en función del ruido')
plt.xlabel('Ruido')
plt.xticks(ruidos)
plt.ylabel('AUC')
plt.grid()
plt.plot(ruidos,AUCs)


    