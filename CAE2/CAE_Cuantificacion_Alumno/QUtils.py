#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

import numpy as np

def dataSetFromQBags(X,Y,bags,n):
    """
    Creates the dataset of the bag n from the dataset (X|Y)
    Params:
        X,Y  : Data Set Attributess/Category
        bags : Bags returned by BagGenerator.generate_bags
        n    : index of the bag in [0, n_bag] , where n_bag is the parameter of 
                BagGenerator
    Returns [Xb,Yb:
        Xb|Yb : bag dataset
    """
    
    # p=bags[0][0][n]
    inds=bags[1][:,n]
    Xb=[]
    Yb=[]
    for i in inds:
        Xb.append(X[i])
        Yb.append(Y[i])
    return [np.array(Xb),np.array(Yb)]