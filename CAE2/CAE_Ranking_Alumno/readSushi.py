#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: quevedo@uniovi.es
"""

# https://preference-learning.org/index.html#Datasets
# https://www.kamishima.net/sushi/

import csv

def getObjetoSushi(row):
    idEje=int(row[0])
    XEje=[]
    for i in range(2,len(row)):
        if i==4: # Minor grouop, hay 12 diferentes del 0 al 11 (ver README-en.txt)
            v=int(row[i])
            for iv in range(12):
                if iv==v:
                    XEje.append(1)
                else:
                    XEje.append(0)
        XEje.append(float(row[i]))
    return [idEje,XEje]
    
def readSushi(fSushi='datasets/sushi/sushi3-2016/sushi3.idata'):
    """
    Lee los datos de sushi y genera los lotes
    Return: [Xshusi Ysushi]
    """
    
    def getLote(Objetos,row,idLote):
        LoteX=[]
        LoteY=[]
        for i in range(len(row)): # Por cada sushi
            v=int(row[i])
            if v>=0:
                LoteX.append(Objetos[i])
                LoteY.append([v,idLote])
        return [LoteX,LoteY]
    
          
    # Leer las descripciones de los objetos (descripciones de sushi)
    Objetos={} # Diccionario de key:idSushi, value:atributos de sushi
    with open(fSushi, newline='') as icsv:
        csvreader = csv.reader(icsv, delimiter='\t')
        for row in csvreader:
            [idEje,XEje]=getObjetoSushi(row)
            
            Objetos[idEje]=XEje
    print('Leídas {} descripciones de sushi'.format(len(Objetos)))
    
    # Leer las puntuaciones y crear el conjunto de datos de ranking
    Xsushi=[]
    Ysushi=[]
    with open('datasets/sushi/sushi3-2016/sushi3b.5000.10.score', newline='') as icsv:
        csvreader = csv.reader(icsv, delimiter=' ')
        idLote=0
        for row in csvreader:
            [LoteX,LoteY]=getLote(Objetos,row,idLote)
            Xsushi=Xsushi+LoteX
            Ysushi=Ysushi+LoteY
            idLote=idLote+1

    print('Creados {} ejemplos valorados a partir de {} lotes'.
          format(len(Ysushi),idLote))
    
    return [Xsushi,Ysushi]
