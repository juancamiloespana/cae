#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

from sklearn.base import BaseEstimator
import numpy as np

class CombiQuanty(BaseEstimator):
    """
    Combina sistemas de cuantifiación prediciendo la media de la prevalencia
    """
    
    def __init__(self,QList):
        """
        Params:
            QList : Lista de cuantificadores (objetos de quantificationlib)
        """
        self.QList=QList
        self.classes_=None
        
    def fit(self,X,Y):
        """
        Entrena todos los sstemas de QList
        """
        
        self.classes_=np.unique(Y) # Always [0,1] in this order
        
        # A) Entrena(fit) los sistemas de self.QList
        ...
            
        return self
    
    def predict(self,X):
        """
        Predice la prevalencia como la media de las prevalencias de cada sistema
        """
        prevs=[0,0]
        for Q in self.QList:
            # B) En pe1 se almacena la prevalencia de la clase 1 para el cuantificador Q
            ...
            prevs[0]=prevs[0]+(1-pe1)
            prevs[1]=prevs[1]+pe1
        prevs[0]=prevs[0]/len(self.QList)
        prevs[1]=prevs[1]/len(self.QList)
        
        return prevs
        
        