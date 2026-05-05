#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema   2 : Cambios en la distribución 
Sesión 1 : Cuantificación
Bloque B : Estimar pérdida en cuantificación
"""

from genToy import genToy
from quantificationlib.baselines.cc import CC
from quantificationlib.baselines.ac import AC,PAC
from quantificationlib.multiclass.df import DFX
from quantificationlib.bag_generator import PriorShift_BagGenerator
from QUtils import dataSetFromQBags
# from cuanti.utils import create_bags_with_multiple_prevalence
import numpy as np
import random
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
# La estimación de funcioners de calidad en 

preTr=0.5  # Prevalencia de entrenamiento
print('Prevalencia de generación: entrenamiento:{:4}'.format(preTr))
RG=random.Random()
RG.seed(1)

# Generar un conjunto de datos
[X,Y]=genToy(RG,1000,prevalencia=preTr)

# Dividirlo en entrenamiento y test
[XTr,XTe,YTr,YTe]=train_test_split(X,Y,test_size=1/3,random_state=1,stratify=Y)

# Crear el modelo de entrenamiento
# Clasificador
Class=SVC(kernel='linear',C=1,probability=True)

# AC
Q=AC(estimator_train=Class, estimator_test=Class)
Q.fit(XTr,YTr)

l1s=[]
# Crear diferentes conjuntos de test con distinta prevalencia
n_bags=100
BG=PriorShift_BagGenerator(n_bags=n_bags,random_state=1)
bags=BG.generate_bags(XTe,YTe)
bags[0]
for i in range(n_bags):
    [Xb,Yb]=dataSetFromQBags(XTe,YTe,bags,i)
    p=np.mean(Yb)
    pres=Q.predict(Xb)
    pe=pres[np.argwhere(Q.classes_==1)[0][0]] # Predicted prevalence
    l1=abs(pe-p)
    print('Prevalencia test:{:6.4f} AC:{:6.4f} l1={:6.4f}'.format(p,pe,l1))
    l1s.append(l1)
print('AC , l1 medio:{:6.4f}\n'.format(np.mean(l1s)))

# Ejericio 1
# Para el sistema DFX para cada uno de los valores de bins [4,8,12] estimar l1 y l2 

# SALIDA:
"""
DFX n_bins: 4 , l1 medio=0.019924  l2 medio=0.000614
DFX n_bins: 8 , l1 medio=0.021082  l2 medio=0.000673
DFX n_bins:12 , l1 medio=0.023663  l2 medio=0.000822
"""

# #<TODO BEGIN Ejercicio 1>


bins=[4,8,12]
l1bins=[]
l2bins=[]

for n_bins in bins:
    Q=DFX(n_bins=n_bins)
    Q.fit(XTr,YTr)
    l1s=[]
    l2s=[]
    # Crear diferentes conjuntos de test con distinta prevalencia
    n_bags=100
    BG=PriorShift_BagGenerator(n_bags=n_bags,random_state=1)
    bags=BG.generate_bags(XTe,YTe)
    for i in range(n_bags):
        [Xb,Yb]=dataSetFromQBags(XTe,YTe,bags,i)
        p=np.mean(Yb)
        pres=Q.predict(Xb)
        pe=pres[np.argwhere(Q.classes_==1)[0][0]] # Predicted prevalence
        l1=abs(pe-p)
        l2=l1**2
        l1s.append(l1)
        l2s.append(l2)
    l1bin=np.mean(l1s)
    l2bin=np.mean(l2s)
    l1bins.append(l1bin)
    l2bins.append(l2bin)
    print('DFX n_bins:{:2} , l1 medio={:8.6f}  l2 medio={:8.6f}'.
          format(n_bins,l1bin,l2bin))
    
# #<TODO END Ejercicio 1>
