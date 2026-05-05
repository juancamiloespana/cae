#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

from sklearn.base import BaseEstimator
import numpy as np

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
        ...
            
        return self
    
    def predict(self,X):
        """
        Predice la prevalencia como la media de las prevalencias de cada sistema
        """
        ranks=[]
        for R in self.RList:
            # B) En rank se almacena el ranking para el sistema R
            ...
            ranks.append(rank)
        avgrank=np.mean(ranks,axis=0)
        
        return avgrank
        
        