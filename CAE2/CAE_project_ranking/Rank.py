#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: quevedo
"""

import numpy as np
from sklearn.svm import LinearSVC
from sklearn.base import BaseEstimator
from sklearn.metrics import roc_auc_score
from sklearn.metrics import ndcg_score



# linearRank class
class linearRank(BaseEstimator):
    """
    Class that learns a linear model that generates a global ranking from 
     batchs of partial ranks.
    """
    def __init__(self,LinealClass=None,verbose=0):
        """
        Params:
            LinealClass : sklearn linear classificator. 
                          Method LinealClass.decision_function must be defined
                          Default=sklearn.svm.LinearSVC(C=1,fit_intercept=False,dual='auto')
            verbose     : integer. if 0 no verbosity.
            
        """
        if LinealClass!=None:
            self.LinealClass=LinealClass
        else:
            self.LinealClass=LinearSVC(C=1,fit_intercept=False,dual='auto')
            
        self.verbose=verbose
    
    def fit(self,X,Y):
        """
        Learns a linear model using the partial ranks of X defined by Y.
        Params:
            X : list of examples. An example is a list of values.
            Y : if Y is a list of values:
                   These values are used to compare examples. The examples with
                   the same value are not compared.
                if Y is a list of lists of two values.
                   The first value is used to campare examples in the batch.
                   The second value is the batchId. All examples with the same bathcId
                    own to the same batch. Each example will be only compared to
                    the examples of their batch.
        """
        
        # Calculate batchs Indices
        [batchs,oneBatch]=linearRank._getBatchsInd(Y)

        if self.verbose>=1:
            print('There are {} batchs of length:'.format(len(batchs)),end='')
            for b in batchs:
                print(' {}'.format(len(b)),end='')
                if self.verbose>=2:
                    print('(indices:',end='')
                    for bi in b:
                        print(' {}'.format(bi),end='')
                    print(')',end='')
            print()
        
        # Generate comparisons
        cX=[]
        cY=[]
        for bInd in batchs:  # for each batch
            if self.verbose>=3:
                print('Batch indices:',end='')
                for b in bInd:
                    print(' {}'.format(b))
                print('')
            for i in range(len(bInd)-1): # for each pair (i,j) of examples in batch
                xi=X[i]
                yi=Y[i] if oneBatch else Y[i][0]
                for j in range(i,len(bInd)):
                    xj=X[j]
                    yj=Y[j] if oneBatch else Y[j][0]
                    if yi!=yj: # There is a comparation
                        cX.append(np.subtract(xi,xj))
                        cY.append(np.sign(yi-yj))
                        cX.append(np.subtract(xj,xi))
                        cY.append(np.sign(yj-yi))
                        if self.verbose>=3:
                            print('  Generated pair (Y[{}]={},Y[{}]={}'
                                  .format())
        if self.verbose>=1:
            print('Generated {} pairs of comparisons'.format(int(len(cX)/2)))
            
        # Learn the model
        self.LinealClass.fit(cX,cY)
        if self.verbose>=1:
            print('Model learned from {} examples.'.format(len(cX)),end='')
            if self.verbose>=2:
                print(' W=',end='')
                for wv in self.LinealClass.coef_[0]:
                    print(' {:6.4f}'.format(wv),end='')
            print()
            
        return self
    
    def predict(self,X):
        """
        Predicts X using the learned model in fit.
        Params:
            X : list of examples. An example is a list of values.
            
        Returns:
            P : list of predictions. Each prediction is a numeric value.
                If example A has a prediction greater than example B 
                 then A is preferred to (ordered before than) B.
        """            
        P=self.LinealClass.decision_function(X)
        if self.verbose>=1:
            print('Predicted {} examples'.format(len(X)))
        return P
    
    def _getBatchsInd(Y):
        if type(Y[0]) not in (list,np.ndarray): # There are no batch Ids
            batchs=[list(range(len(Y)))] # There are only one batch
            oneBatch=True
            return [batchs,oneBatch]
            
        # There are batch Ids
        Bn=np.array(list(map(lambda p:p[1],Y))) # Batchs numbers
        B=np.unique(Bn) # Different batchs
        
        batchs=[]
        for b in B:
            batchs.append(np.where(Bn==b)[0].tolist())
        
        oneBatch=False
        return [batchs,oneBatch]
    
# Measures

def CIndex(Y,P):
    """
    Calculates a C-index (concordance index) measure 
    C-index is calculated as the proportion of corrected ordered pair of examples
    https://proceedings.neurips.cc/paper/2007/file/33e8075e9970de0cfea955afd4644bb2-Paper.pdf
    
    Params
        Y : list of values, real values.
        P : list of values, predictions.
        
    Returns
        C-Index value. The proportion of all ordered pairs in Y that concordance
         (same order) in P
        If Y is void or all values or Y are the same (no ordered pairs) None is returned 
    """ 
    E=len(Y) # number of examples
    Ci=0
    nPairs=0
    for i in range(E-1):
        for j in range(i,E):
            if Y[i]!=Y[j]: # There is a pair that is ordered
                nPairs=nPairs+1
                if P[i]==P[j]:  # If tie
                    Ci=Ci+0.5 # half sucess (0.5 of 1)
                elif np.sign(P[i]-P[j])==np.sign(Y[i]-Y[j]): # Same order
                    Ci=Ci+1 # Full sucess (1 of 1)
    if nPairs==0:
        return None
    else:
        return Ci/nPairs
    

# multiBatch measures base class
class multiBatch:
    """
    Class for apply a ranking measure in a multi batch test
    """
    def __init__(self,rankMeasure,*,ponderation='one'):
        """
        Params:
            - rankMeasure : rankMeasure(y_true, y_score) -> Number
                            callable that evaluates the quality of a batch given 
                            the real rank values (y_true) and then predicted ones (y_score)
            - ponderation : The __call__ method returns the ponderated average of the 
                            measures of each batch. This param defines the ponderation.
                            'one'   : ponderate each batch by one that means use the mean of each batch
                            'pairs' : ponderate each batch by the number of pairs with different rank value
                            callable: given the batch as a list of y_true values of the batch returns the batch's ponderation
                                      if a ponderation is < 0 an exception will be raised
        """
        self.rankMeasure=rankMeasure
        self.ponderation=ponderation
        self.__name__=str(rankMeasure)
        
    def __call__(self,y_true, y_score):
        """
        Apply rankMeasure to each batch
        if rankMeasure returns None for a batch, this batch will be not used
        if rankMeasure returns None for all batchs, if will
        Params:
            - y_true  : list of pairs [rank value,batch]
            - y_score : list of rank values
            
        Returns:
            average of each no None rankMeasure ponderated by the given ponderation
            None if all rankMeasures are None or all poderations are 0
        """
        # Get the batchs ids
        y_true =np.array(y_true)
        y_score=np.array(y_score)
        batchs=np.unique(y_true[:,1])
        
        # To store measures and poderations of each batch
        measures=[] 
        ponderas=[]
        for bNumber in batchs:
            # Get the batch's true values and scores
            batchVals =y_true[y_true[:,1]==bNumber][:,0]
            batchScore=y_score[y_true[:,1]==bNumber]
            
            # Calculate score and ponderation and store if measure is not None
            batchMeasure=self.rankMeasure(batchVals,batchScore)
            if batchMeasure is not None:
                batchPondera=self._ponderation(batchVals)
                if batchPondera<0:
                    raise Exception('multiBatch ponderation returns a negative value')
                measures.append(batchMeasure)
                ponderas.append(batchPondera)
                
        if len(measures)==0: # All measures are None
            return None
        
        if sum(ponderas)==0: # All poderations are 0
            return None
        
        # Returns the weighted mean
        return np.average(measures,weights=ponderas)
        

    def _ponderation(self,batchVals):
        if type(self.ponderation)==str:
            if self.ponderation=='one':
                return 1
            if self.ponderation=='pairs':
                return multiBatch._calculatePairs(batchVals)
            raise(Exception('multiBatch ponderation value "{}" not allowed'.format(self.ponderation)))
        if hasattr(self.ponderation,'__call__'): # it is callable
            return self.ponderation(batchVals)
        raise(Exception('multiBatch ponderation error'.format(self.ponderation)))
            
    def _calculatePairs(vals):
        n=0
        for i in range(len(vals)-1):
            for j in range(i+1,len(vals)):
                if vals[i]!=vals[j]:
                    n=n+1
        return n

multiBatchAUC   =multiBatch(roc_auc_score,ponderation='pairs')
multiBatchCIndex=multiBatch(CIndex,ponderation='pairs')
multiBatchNDCG=multiBatch(lambda Y,P:ndcg_score([Y],[P]),ponderation='pairs')



# Utils

# Aggregate batchs
def aggregateBatchDataSets(*batchDSs):
    """
    Create a newdataset aggregating all the batchs with consecutive batch numbers
    Params:
        batchDSs : list of [value,batch]
    """
    newBatchDS=[]
    bnDict={}
    for ibatchDS in range(len(batchDSs)):
        batchDS=batchDSs[ibatchDS]
        for [val,batch] in batchDS:  
            key='{}_{}'.format(ibatchDS,batch)
            if key in bnDict.keys():
                bn=bnDict[key]
            else:
                bn=len(bnDict)
                bnDict[key]=bn
            newBatchDS.append([val,bn])
    return newBatchDS            
# Example of use
if __name__=='__main__':
    YDS1=[[1,0],[3,0],[1,1],[2,1]]
    YDS2=[[2,0],[5,0],[2,0],[2,1],[4,1],[4,1],[1,3],[2,3],[2,3]]
    YDS3=[[1,0],[1,0],[2,0]]
    newYDS=aggregateBatchDataSets(YDS1,YDS2,YDS3)
    print('NewYDS:')
    for vb in newYDS:
        print(vb)
        

class SKWrapperXGBRanker(BaseEstimator):
    """
    Wrapper of a XGBRanker into sklearn enviroment with [value,batch] values at Y
    """
    def __init__(self,xgbranker):
        """
        Param:
            xgbranker : a XGBRanker object
        """
        self.xgbranker=xgbranker
        
    def getXGBRanker(self):
        return self.xgbranker
        
    def fit(self,X,Y):
        """
        Transforms Y from a list of [value,batch] to use in XGBRanker.fit and call it
        Reorder the examples to get an ordered qid list
        """        
        Y=np.array(Y)
        X=np.array(X)
        
        # Get the arrays
        xgY=Y[:,0]
        qid=Y[:,1]
        
        # Reorder
        order=np.argsort(qid)
        X=X[order]
        xgY=xgY[order]
        qid=qid[order]
        
        return self.xgbranker.fit(X,xgY,qid=qid)
    
    def predict(self,X):
        return self.xgbranker.predict(X)
