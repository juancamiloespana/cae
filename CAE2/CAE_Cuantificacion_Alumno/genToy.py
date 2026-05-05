#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def genToy(RG,nEjemplos,prevalencia,media0=[-1,-1],media1=[+1,+1],dt0=[1,1],dt1=[1,1]):
    """
    Genera un conjunto de datos en 2 dimensiones con categoría 0 ó 1
    Los valores de los atributos se generan a partir de distribuciones normales
    
    Parámetros:
        - RG          : objeto random.Random() 
        - nEjemplos   : número de objetos que genera
        - prevalencia : proporción de ejemplos de la clase positiva (1)
        - media0,dt0  : media y desviación típica de los ejemplos de la clase 0 para cada atributo
        - media1,dt1  : media y desviación típica de los ejemplos de la clase 1 para cada atributo
    
    Retorna:
        [X,Y] : conjunto de datos donde
                X es matriz nEjemplos x 2 con valoren numéricos
                Y es vector de nEjemplos con valores 0 o 1

    """
    X=[]
    Y=[]
    ePos=int(nEjemplos*prevalencia)
    eNeg=nEjemplos-ePos
    for e in range(eNeg):
        x=[RG.normalvariate(media0[0],dt0[0]),RG.normalvariate(media0[1],dt0[1])]
        X.append(x)
        Y.append(0)
    for e in range(ePos):
        x=[RG.normalvariate(media1[0],dt1[0]),RG.normalvariate(media1[1],dt1[1])]
        X.append(x)
        Y.append(1)
    return  [np.array(X),np.array(Y)]