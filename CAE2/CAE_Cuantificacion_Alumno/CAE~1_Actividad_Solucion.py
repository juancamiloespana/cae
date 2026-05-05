#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema      2 : Problemas Complejos de Aprendizaje Supervisado 
Sesión    1 : Cuantificación
Actividad 1
"""

# Actividad 1

# DATOS:
# Los datos de origen son de setas:
# https://archive.ics.uci.edu/ml/datasets/mushroom
# Hay dos categorías: venenosa:0 y  comestible:1
# Los datos han sido recogidos de una manera tal que la prevalencia de la primera
#mitad (entrenamiento) es diferente a la segunda (test). 
# Puede que influya estacionalidad o localización.
# Los datos se leen en las variables:
# XTr , YTr : Entrenamiento
# XTe , YTe : Test


# Datos:
import csv
import numpy as np

def leecsv(FName):
    M=[]
    with open(FName, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            if len(row)==1:
                M.append(int(row[0]))
            else:
                R=[]
                for v in row:
                    R.append(int(v))
                M.append(R)
    return np.array(M)



from sklearn.svm import SVC
from quantificationlib.baselines.cc import CC
from quantificationlib.baselines.ac import PAC

XTr=leecsv('cuantiDataSets/agaricus-lepiota-XTr.csv')
YTr=leecsv('cuantiDataSets/agaricus-lepiota-YTr.csv')
XTe=leecsv('cuantiDataSets/agaricus-lepiota-XTe.csv')
YTe=leecsv('cuantiDataSets/agaricus-lepiota-YTe.csv')

PreTr=np.mean(YTr)
PreTe=np.mean(YTe)

print('Prevalencia Entrenamiento:{:6.4f}  test:{:6.4f}'.format(PreTr,PreTe))


# CLASIFICADOR:
# El objetivo de esta actividad es comprobar como un mal clasificador puede ser
#usado para obtener buenos resultados de cuantificación.
# Se usará un SVC con kernel lineal y C=10**-4. Este clasificador predice siempre
#1 -> comestible. Claramente no es un buen clasificador

# Clasificador:
Class=SVC(kernel='linear',C=10**-4,probability=True)



# ENUNCIADO
# Evaluar la prevalencia del test usando CC y PAC.
# En ambos casos calcular el las funciones de pérdida l1 y l2

# SALIDA:
# Prevalencia Entrenamiento:0.8188  test:0.2171
# Prevalencia estimada con CC           :1.0000
#     Calidad de la estimación: l1=0.7829  l2=0.6129
# Prevalencia estimada con PAC          :0.1902
#     Calidad de la estimación: l1=0.0270  l2=0.0007     



#<TODO BEGIN Actividad 1>

# Cuantificacación usando CC
Q=CC(Class)
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]

print('\nPrevalencia evaluada con CC           :{:6.4f}'.format(pre))

# Error l1 y l2
l1=abs(PreTe-pre)
l2=l1**2

print('    Calidad de la evaluación: l1={:6.4f}  l2={:6.4f}'.format(l1,l2))


# Cuantificacación usando PAC
Q=PAC(estimator_train=Class, estimator_test=Class)
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]

print('Prevalencia estimada con PAC          :{:6.4f}'.format(pre))

# Error l1 y l2
l1=abs(PreTe-pre)
l2=l1**2

print('    Calidad de la estimación: l1={:6.4f}  l2={:6.4f}'.format(l1,l2))


#<TODO END Actividad 1>

# Actividad 2
# Para el conjunto de ENTRENAMIENTO anterior (Sin el test), 
# Realizar un proceso por el que se indique qué sistema (CC o PAC) es mejor

# SALIDA (Según corresponda):
# Es mejor {CC|PAC} 

#<TODO BEGIN Actividad 2>
from sklearn.model_selection import train_test_split
from quantificationlib.bag_generator import PriorShift_BagGenerator
from QUtils import dataSetFromQBags

print('Datos de entrenamiento: Ejemplos:{} Prevalencia:{:6.4f}'.format(len(XTr),np.mean(YTr)))

# Dividirlo el entrenamiento entrenamiento2 (Tr2) y test2 (Te2)
# Se hace estratificado (misma prevalencia en la partición)
[XTr2,XTe2,YTr2,YTe2]=train_test_split(XTr,YTr,test_size=1/3,random_state=1,stratify=YTr)

print('Datos partición')
print('       - train2 Ejemplos:{} Prevalencia:{:6.4f}'.format(len(XTr2),np.mean(YTr2)))
print('       - test2  Ejemplos:{} Prevalencia:{:6.4f}'.format(len(XTe2),np.mean(YTe2)))

print('\nEstimando calidad para CC')
Q=CC(Class)
Q.fit(XTr2,YTr2)
l1s=[] # Utilizo l1, pero estaría igual de bien utilizar l2
n_bags=100
BG=PriorShift_BagGenerator(n_bags=n_bags,random_state=1)
bags=BG.generate_bags(XTe2,YTe2)
for i in range(n_bags):
    [Xb,Yb]=dataSetFromQBags(XTe2,YTe2,bags,i)
    p=np.mean(Yb)
    pres=Q.predict(Xb)
    pe=pres[np.argwhere(Q.classes_==1)[0][0]] # Predicted prevalence
    l1=abs(pe-p)
    print('{:2}/{:2} Prevalencia test:{:6.4f} CC:{:6.4f} l1={:6.4f}'
          .format(i,n_bags-1,p,pe,l1))
    l1s.append(l1)
CCl1=np.mean(l1s)
print('CC , l1 medio:{:6.4f}\n'.format(CCl1))

print('\nEstimando calidad para PAC')
Q=PAC(estimator_train=Class, estimator_test=Class)
Q.fit(XTr2,YTr2)
l1s=[]
n_bags=100
BG=PriorShift_BagGenerator(n_bags=n_bags,random_state=1)
bags=BG.generate_bags(XTe2,YTe2)
for i in range(n_bags):
    [Xb,Yb]=dataSetFromQBags(XTe2,YTe2,bags,i)
    p=np.mean(Yb)
    pres=Q.predict(Xb)
    pe=pres[np.argwhere(Q.classes_==1)[0][0]] # Predicted prevalence
    l1=abs(pe-p)
    print('{:2}/{:2} Prevalencia test:{:6.4f} PAC:{:6.4f} l1={:6.4f}'
          .format(i,n_bags-1,p,pe,l1))
    l1s.append(l1)
PACl1=np.mean(l1s)
print('PAC , l1 medio:{:6.4f}\n'.format(PACl1))

print('Es mejor ',end='')
if CCl1<PACl1:
    print('CC')
else:
    print('PAC')



