#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema   2 : Cambios en la distribución 
Sesión 1 : Cuantificación
Bloque A : Problemas de cuantificación
"""

from genToy import genToy

from quantificationlib.baselines.cc import CC
from quantificationlib.baselines.ac import AC,PAC
from quantificationlib.multiclass.df import DFX


import numpy as np
import random
from sklearn.svm import SVC
import matplotlib.pyplot as plt

# Generar conjuntos con diferente prevalencia en entrenamiento que en test

preTr=0.5  # Prevalencia de entrenamiento
preTe=0.05 # Prevalencia de test
print("hola")
print('Prevalencia de generación: entrenamiento: {} test : {}'.format(preTr,preTe))
RG=random.Random()
RG.seed(1)
[XTr,YTr]=genToy(RG,100,prevalencia=preTr) # Mirar genToy.py
[XTe,YTe]=genToy(RG,100,prevalencia=preTe)

# Representación gráfica
def pintaXY(X,Y,ax,tit,color0,color1):
    iPos=np.nonzero(Y)[0] # índices positivos
    iNeg=np.nonzero(Y-1)[0] # índices negativos
    
    ax.set_title(tit)
    ax.set_xlim([-4,+4])
    ax.set_ylim([-4,+4])
    ax.set_xlabel('Atributo 0')
    ax.set_ylabel('Atributo 1')
    ax.plot(X[iPos,0],X[iPos,1],'o',color=color1,label='Pos')
    ax.plot(X[iNeg,0],X[iNeg,1],'o',color=color0,label='Neg')
    if color0!=color1:
        ax.legend()

fig,axs=plt.subplots(1,2,figsize=[6,3],layout='tight')
pintaXY(XTr,YTr,axs[0],'Entrenamiento\nPrevalencia={}'.format(preTr),color0='blue',color1='green') 
pintaXY(XTe,YTe,axs[1],'Test (Sin categoría)\nPrevalencia=¿?',color0='grey',color1='grey') 
plt.savefig('CuantiEntrenamiento.pdf')

fig=plt.figure(figsize=[3,3],layout='tight')
pintaXY(XTe,YTe,plt.axes(),'Test\nPrevalencia={}'.format(preTe),color0='blue',color1='green') 
plt.savefig('CuantiTest.pdf')

# Proceso de cuantificación

# Clasificador
Class=SVC(kernel='linear',C=1,probability=True)
Class.fit(XTr,YTr) # Modelo

# Clasificación del test 
ClaTe=Class.predict(XTe)
ClaTe.mean()
ClaTr=Class.predict(XTr)
ClaTr.mean()



# Estimación de probabilidad del entrenamiento y del test 
ProTr=Class.predict_proba(XTr)
ProTe=Class.predict_proba(XTe)

Class.classes_

ProTr.mean(axis=0)
ProTe.mean(axis=0)

Nombres=['CC','AC','PAC','HFX']
PE=[None]*4 # Prevalencia estimada de cada algoritmo

# Estimar la prevalencia con los diferentes algoritmos de cuantificación
# CC 
Q=CC(estimator_test=Class)
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]
PE[0]=pre



# AC
Q=AC(estimator_train=Class, estimator_test=Class)
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]
PE[1]=pre

# PAC
Q=PAC(estimator_train=Class, estimator_test=Class)
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]
PE[2]=pre

# HDX
Q=DFX()
Q.fit(XTr,YTr)
pres=Q.predict(XTe)
pre=pres[np.argwhere(Q.classes_==1)[0][0]]
PE[3]=pre

# Calculo del valor de pérdida

# Cálculo de P. Te. (Prevalencia del test)
PTe=len(np.nonzero(YTe)[0])/len(YTe)
print('Prevalencia obtenida del test        : {:6.4f}'.format(PTe))

# Imprimir la PE y el valor de pérdida para algoritmo de cuantificación
# l1 : distancia lineal, norma 1 (diferencia en valor absoluto)
# l2 : distancia cuadrática, norma 2 (diferencia al cuadrado)
for iac in range(len(PE)):
    pre=PE[iac]
    print('Prevalencia del test estimada con {:3}: {:6.4f} l1={:6.4f} l2={:6.4f}'
          .format(Nombres[iac],pre,abs(pre-PTe),(pre-PTe)**2))

# Ejercicio 1
# Para el experimento anterior variar la prevalencia del conjunto de test de
#0,05 a 0,95 con paso 0,05.
# Calcular la pérdida l1 y l2 para los 4 sistemas de cuantificación e imprimirla
# Optativo:
# Almacenar los valores l1 y hacer una gráfica

# SALIDA:
"""
Prevalencia obtenida del test        : 0.0500
Prevalencia del test estimada con CC : 0.1600 l1=0.1100 l2=0.0121
Prevalencia del test estimada con AC : 0.0476 l1=0.0024 l2=0.0000
Prevalencia del test estimada con PAC: 0.0557 l1=0.0057 l2=0.0000
Prevalencia del test estimada con HDy: 0.0911 l1=0.0411 l2=0.0017

Prevalencia obtenida del test        : 0.1000
Prevalencia del test estimada con CC : 0.1400 l1=0.0400 l2=0.0016
Prevalencia del test estimada con AC : 0.0238 l1=0.0762 l2=0.0058
Prevalencia del test estimada con PAC: 0.0689 l1=0.0311 l2=0.0010
Prevalencia del test estimada con HDy: 0.1059 l1=0.0059 l2=0.0000

Prevalencia obtenida del test        : 0.1500
Prevalencia del test estimada con CC : 0.2500 l1=0.1000 l2=0.0100
Prevalencia del test estimada con AC : 0.1548 l1=0.0048 l2=0.0000
Prevalencia del test estimada con PAC: 0.1610 l1=0.0110 l2=0.0001
Prevalencia del test estimada con HDy: 0.1705 l1=0.0205 l2=0.0004

Prevalencia obtenida del test        : 0.2000
Prevalencia del test estimada con CC : 0.2800 l1=0.0800 l2=0.0064
Prevalencia del test estimada con AC : 0.1905 l1=0.0095 l2=0.0001
Prevalencia del test estimada con PAC: 0.1997 l1=0.0003 l2=0.0000
Prevalencia del test estimada con HDy: 0.1892 l1=0.0108 l2=0.0001

Prevalencia obtenida del test        : 0.2500
Prevalencia del test estimada con CC : 0.3400 l1=0.0900 l2=0.0081
Prevalencia del test estimada con AC : 0.2619 l1=0.0119 l2=0.0001
Prevalencia del test estimada con PAC: 0.2755 l1=0.0255 l2=0.0006
Prevalencia del test estimada con HDy: 0.3138 l1=0.0638 l2=0.0041

Prevalencia obtenida del test        : 0.3000
Prevalencia del test estimada con CC : 0.3600 l1=0.0600 l2=0.0036
Prevalencia del test estimada con AC : 0.2857 l1=0.0143 l2=0.0002
Prevalencia del test estimada con PAC: 0.2995 l1=0.0005 l2=0.0000
Prevalencia del test estimada con HDy: 0.3360 l1=0.0360 l2=0.0013

Prevalencia obtenida del test        : 0.3500
Prevalencia del test estimada con CC : 0.3800 l1=0.0300 l2=0.0009
Prevalencia del test estimada con AC : 0.3095 l1=0.0405 l2=0.0016
Prevalencia del test estimada con PAC: 0.3267 l1=0.0233 l2=0.0005
Prevalencia del test estimada con HDy: 0.3233 l1=0.0267 l2=0.0007

Prevalencia obtenida del test        : 0.4000
Prevalencia del test estimada con CC : 0.4300 l1=0.0300 l2=0.0009
Prevalencia del test estimada con AC : 0.3690 l1=0.0310 l2=0.0010
Prevalencia del test estimada con PAC: 0.3893 l1=0.0107 l2=0.0001
Prevalencia del test estimada con HDy: 0.3701 l1=0.0299 l2=0.0009

Prevalencia obtenida del test        : 0.4500
Prevalencia del test estimada con CC : 0.4900 l1=0.0400 l2=0.0016
Prevalencia del test estimada con AC : 0.4405 l1=0.0095 l2=0.0001
Prevalencia del test estimada con PAC: 0.4659 l1=0.0159 l2=0.0003
Prevalencia del test estimada con HDy: 0.4863 l1=0.0363 l2=0.0013

Prevalencia obtenida del test        : 0.5000
Prevalencia del test estimada con CC : 0.5200 l1=0.0200 l2=0.0004
Prevalencia del test estimada con AC : 0.4762 l1=0.0238 l2=0.0006
Prevalencia del test estimada con PAC: 0.4926 l1=0.0074 l2=0.0001
Prevalencia del test estimada con HDy: 0.5060 l1=0.0060 l2=0.0000

Prevalencia obtenida del test        : 0.5500
Prevalencia del test estimada con CC : 0.5600 l1=0.0100 l2=0.0001
Prevalencia del test estimada con AC : 0.5238 l1=0.0262 l2=0.0007
Prevalencia del test estimada con PAC: 0.5049 l1=0.0451 l2=0.0020
Prevalencia del test estimada con HDy: 0.5371 l1=0.0129 l2=0.0002

Prevalencia obtenida del test        : 0.6000
Prevalencia del test estimada con CC : 0.6100 l1=0.0100 l2=0.0001
Prevalencia del test estimada con AC : 0.5833 l1=0.0167 l2=0.0003
Prevalencia del test estimada con PAC: 0.5858 l1=0.0142 l2=0.0002
Prevalencia del test estimada con HDy: 0.5723 l1=0.0277 l2=0.0008

Prevalencia obtenida del test        : 0.6500
Prevalencia del test estimada con CC : 0.6300 l1=0.0200 l2=0.0004
Prevalencia del test estimada con AC : 0.6071 l1=0.0429 l2=0.0018
Prevalencia del test estimada con PAC: 0.5958 l1=0.0542 l2=0.0029
Prevalencia del test estimada con HDy: 0.6056 l1=0.0444 l2=0.0020

Prevalencia obtenida del test        : 0.7000
Prevalencia del test estimada con CC : 0.6800 l1=0.0200 l2=0.0004
Prevalencia del test estimada con AC : 0.6667 l1=0.0333 l2=0.0011
Prevalencia del test estimada con PAC: 0.6736 l1=0.0264 l2=0.0007
Prevalencia del test estimada con HDy: 0.6793 l1=0.0207 l2=0.0004

Prevalencia obtenida del test        : 0.7500
Prevalencia del test estimada con CC : 0.7500 l1=0.0000 l2=0.0000
Prevalencia del test estimada con AC : 0.7500 l1=0.0000 l2=0.0000
Prevalencia del test estimada con PAC: 0.7620 l1=0.0120 l2=0.0001
Prevalencia del test estimada con HDy: 0.7285 l1=0.0215 l2=0.0005

Prevalencia obtenida del test        : 0.8000
Prevalencia del test estimada con CC : 0.8100 l1=0.0100 l2=0.0001
Prevalencia del test estimada con AC : 0.8214 l1=0.0214 l2=0.0005
Prevalencia del test estimada con PAC: 0.7959 l1=0.0041 l2=0.0000
Prevalencia del test estimada con HDy: 0.8141 l1=0.0141 l2=0.0002

Prevalencia obtenida del test        : 0.8500
Prevalencia del test estimada con CC : 0.7900 l1=0.0600 l2=0.0036
Prevalencia del test estimada con AC : 0.7976 l1=0.0524 l2=0.0027
Prevalencia del test estimada con PAC: 0.7973 l1=0.0527 l2=0.0028
Prevalencia del test estimada con HDy: 0.8137 l1=0.0363 l2=0.0013

Prevalencia obtenida del test        : 0.9000
Prevalencia del test estimada con CC : 0.8500 l1=0.0500 l2=0.0025
Prevalencia del test estimada con AC : 0.8690 l1=0.0310 l2=0.0010
Prevalencia del test estimada con PAC: 0.8860 l1=0.0140 l2=0.0002
Prevalencia del test estimada con HDy: 0.9082 l1=0.0082 l2=0.0001

Prevalencia obtenida del test        : 0.9500
Prevalencia del test estimada con CC : 0.8600 l1=0.0900 l2=0.0081
Prevalencia del test estimada con AC : 0.8810 l1=0.0690 l2=0.0048
Prevalencia del test estimada con PAC: 0.8882 l1=0.0618 l2=0.0038
Prevalencia del test estimada con HDy: 0.8994 l1=0.0506 l2=0.0026
"""

#<TODO BEGIN Ejercicio 1>

l1s=[] # Almacena todas las pérdidas l1
PorPreTes=list(range(5,100,5))
for PorPreTe in PorPreTes: # Porcentaje de prevalencia de test
    preTe=PorPreTe/100 # Prevalencia en proporcion
    [XTe,YTe]=genToy(RG,100,prevalencia=preTe)
    
    # Estimación de clasificación del test 
    ClaTe=Class.predict(XTe)
    
    # Estimación de probabilidad del test 
    ProTe=Class.predict_proba(XTe)
    
    # Estimar la prevalencia con los diferentes algoritmos de cuantificación
    # CC 
    Q=CC(estimator_test=Class)
    Q.fit(XTr,YTr)
    pres=Q.predict(XTe)
    pre=pres[np.argwhere(Q.classes_==1)[0][0]]
    PE[0]=pre
    
    # AC
    Q=AC(estimator_train=Class, estimator_test=Class)
    Q.fit(XTr,YTr)
    pres=Q.predict(XTe)
    pre=pres[np.argwhere(Q.classes_==1)[0][0]]
    PE[1]=pre
    
    # PAC
    Q=PAC(estimator_train=Class, estimator_test=Class)
    Q.fit(XTr,YTr)
    pres=Q.predict(XTe,predictions_test=ProTe)
    pre=pres[np.argwhere(Q.classes_==1)[0][0]]
    PE[2]=pre
    
    # HDy
    Q=DFX()
    Q.fit(XTr,YTr)
    pres=Q.predict(XTe)
    pre=pres[np.argwhere(Q.classes_==1)[0][0]]
    PE[3]=pre
    

    # Cálculo de P. Te. (Prevalencia del test)
    PTe=len(np.nonzero(YTe)[0])/len(YTe)
    print('\nPrevalencia obtenida del test        : {:6.4f}'.format(PTe))
    
    # Imprimir la PE y el valor de pérdida para algoritmo de cuantificación
    # l1 : distancia lineal, norma 1 (diferencia en valor absoluto)
    # l2 : distancia cuadrática, norma 2 (diferencia al cuadrado)
    l1sc=[None]*4 # l1 para sistema de cuentificación
    for iac in range(len(PE)):
        pre=PE[iac]
        print('Prevalencia del test estimada con {:3}: {:6.4f} l1={:6.4f} l2={:6.4f}'
              .format(Nombres[iac],pre,abs(pre-PTe),(pre-PTe)**2))
        l1sc[iac]=abs(pre-PTe)
    
    l1s.append(l1sc) # Almacenar las l1 de cada sistema
    
# Gráfica
l1s=np.array(l1s) # Lo convierto a numpy.ndarray para poder seleccionar columnas
PreTes=list(map(lambda x:x/100,PorPreTes)) # Dividir entre 100 cada Porcentaje de Prevalencia
plt.figure()
for iac in range(len(PE)):
    plt.plot(PreTes,l1s[:,iac],label=Nombres[iac])
plt.legend()      
plt.xticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9])
plt.xlabel('Prevalencia')
plt.ylabel('l1')
plt.savefig('Prevalencia_l1_4Algoritmos.pdf')
#<TODO END Ejercicio 1>

