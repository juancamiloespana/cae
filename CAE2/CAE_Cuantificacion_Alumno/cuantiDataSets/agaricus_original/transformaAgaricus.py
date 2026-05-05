#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""


import csv
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# Leer
M=[]
with open('agaricus-lepiota.data', newline='') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        M.append(row)

# Eliminar valores desconocidos
M=np.array(M)
Y=M[:,0]
X=np.delete(M,11,1) # Eliminar atributo con valores desconocidos

# Simbólico a numérico
enc = OneHotEncoder()
enc.fit(X)
XNum=np.array(enc.transform(X).todense().tolist())
YNum=list(map(lambda x:0 if x=='p' else 1,Y))

print('Leidos       : {} ejemplos. Prevalencia={:6.4f}'.format(len(YNum),np.mean(YNum)))


# Dividir entrenamiento y test
Thres=4062 # Donde se divide entrenamiento y test

YNumTr=YNum[:Thres]
XNumTr=XNum[:Thres]
print('Entrenamiento: {} ejemplos. Prevalencia={:6.4f}'.format(len(YNumTr),np.mean(YNumTr)))

YNumTe=YNum[Thres:]
XNumTe=XNum[Thres:]
print('test         : {} ejemplos. Prevalencia={:6.4f}'.format(len(YNumTe),np.mean(YNumTe)))


# Escribir
def writecsv(FName,M):
    with open(FName,'wt') as csvfile:
        for row in M:
            if type(row)==int:
                row=[row]
            first=True
            for v in row:
                if first:
                    first=False
                else:
                    csvfile.write(',')
                csvfile.write('{:g}'.format(v))
            csvfile.write('\n')

writecsv('agaricus-lepiota-XTr.csv',XNumTr)
writecsv('agaricus-lepiota-YTr.csv',YNumTr)
writecsv('agaricus-lepiota-XTe.csv',XNumTe)
writecsv('agaricus-lepiota-yTe.csv',YNumTe)



