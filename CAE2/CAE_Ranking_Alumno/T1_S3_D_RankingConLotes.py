# -*- coding: utf-8 -*-
"""
Tema   1 : Problemas Complejos de Aprendizaje Supervisado 
Sesión 3 : Ranking
Bloque D : Aprendizaje de ranking con varios lotes
"""

# 
# Como se indicó en el bloque A, los conjuntos de ejemplos de ranking están agrupados
#por lotes. Solo los objetos del mismo lote formarán pares (preferencias)


# Ejemplo restaurantes

# Datos del bloque A
# Restaurantes
R1=[9.4,  5.0]
R2=[0.5, -1]
R3=[3.5,  0]
R4=[7.5,  2.3]

X=[R2    ,R1    ,R2    ,R4    ,R3    ,R1    ,R2    ,R3    ,R4    ,R1]
Y=[[2,1] ,[1,1] ,[3,2] ,[2,2] ,[2,2] ,[1,2] ,[4,3] ,[3,3] ,[2,3] ,[1,3]]

# Restaurantes a ordenar y sus nombres (test)
RN1=[7.4,  6]
RN2=[4.5,  0.5]
RN3=[0.9, -2.5]
RN4=[2.6,  2.9]
RN5=[6.0,  4.6]

Nombres=['RN1','RN2','RN3','RN4','RN5']

# Partiendo del ejemplo de los restuarantes (Bloque A) se quieren ordenar cinco
#nuevos restaurantes (RN*) de los que no hay críticas. 
# Detallar el proceso e imprimir el nombre los restaurantes nuevos de mejor a peor
#junto con su valoración del ranking

# SOLUCIÓN:

# Crear un modelo de ranking con los datos del bloque A
from CAE_project_ranking.Rank import linearRank
Ranker=linearRank()
Ranker.fit(X,Y)

# Crear el conjunto de test y evaluarlo con el modelo anterior
XTe=[RN1,RN2,RN3,RN4,RN5]
P=Ranker.predict(XTe)

# Ordenar de mayor puntuación a menor e imprimir la valoración del ranking
import numpy as np
orden=np.argsort(-P) # Como artgsort ordena de menos a más, se cambia el signo de P para que ordene P de más a menos    
for i in orden:
    print('{} valor ranking:{:+6.4f}'.format(Nombres[i],P[i]))

# Medida del error

# Un grupo de críticos ha valorado algunos de los nuevos restaurantes.
#Calcular una medida de calidad para la predicción anterior (P) tomando como
# correcto(Y) lo valorado por los criticos:
    
# Valoraciónes de los críticos
# Cada fila es un crítico y las 5 columnas son los 5 restaurantes.
#Cada crítico solo valoró (cuanto más mejor) alguno de los restaurantes, 
# si no hay valoración se indica con None

Valoraciones=[
    #RN1 ,RN2 ,RN3 ,RN4 ,RN5  <- Restaurante (Objeto)
    [3   ,None,None,4   ,2],  # Crítico 1
    [2   ,4   ,None,None,8],  # Crítico 2
    [None,27  ,53  ,45  ,27]] # Crítico 3

# SOLUCIÓN:

# Por cada Crítico se crea un lote con los restaurantes que ha valorado.
# Se añaden a YTe el par [valoración,lote], donde como lote se tome el
# En XTe se indican los atributos del restaurante

YTe=[[3,1],[4,1],[2,1],[2,2],[4,2],[8,2],[27,3],[53,3],[45,3],[27,3]]
XTe=[RN1  ,RN4  ,RN5  ,RN1  ,RN2  ,RN5  ,RN2   ,RN3   ,RN4   ,RN5   ]

# Se evalúa
PTe=Ranker.predict(XTe)

# No necesario, solo a efectos de mostar información
XTeNames=['RN1'  ,'RN4'  ,'RN5'  ,'RN1'  ,'RN2'  ,'RN5'  ,'RN2'   ,'RN3'   ,'RN4'   ,'RN5'   ]

for i in range(len(PTe)):
    print('{} valor ranking:{:+6.4f}'.format(XTeNames[i],PTe[i]))

# Como es multi-evaluado se utilizará CIndex y como hay lotes se utilizará:
from CAE_project_ranking.Rank import multiBatchCIndex

ResCI=multiBatchCIndex(YTe,PTe)

print('\nCIndex de las valoraciones del modelo sobre los nuevos restaurantes={:6.4f}'
      .format(ResCI))

# Ejercicio 1

# El restaurante NR6 gusta más que el NR7. Entrena un modelo con los datos
#de los restaurantes del bloque A (X,Y) y los nuevos (XTe,YTe), evalúa NR6 y NR7 e
# imprime los valores de ranking que ha predicho el modelo.
#Comprueba si este modelo es coherente con NR6 >~ NR7

NR6=[3.5, 0.5]
NR7=[6.1, 4.7]

#<TODO BEGIN Ejercicio 1>

# Juntar (X,Y) con (XTe,YTe): no se puede hacer concatenando, pues los lotes Y e YTe
#que tengan el mismo número se tomarán como el mismo lote cuando no lo son.
# Solución: utilizar aggregateBatchDataSets que renombra automáticamente los batchs

from CAE_project_ranking.Rank import aggregateBatchDataSets
XTodoTr=X+XTe # Suponemos de tipo list
YTodoTr=aggregateBatchDataSets(Y,YTe) # Renombra los números de los batchs (míralo)

# Creación del test
XTodoTe=[NR6  ,NR7]
YTodoTe=[[2,0],[1,0]]

# Entrenar el modelo
Ranker=linearRank()
Ranker.fit(XTodoTr,YTodoTr)

# Evaluar el conjunto de test 
PTodoTe=Ranker.predict(XTodoTe)

print('Valor de ranking para NR6:{:+6.4f}'.format(PTodoTe[0]))
print('Valor de ranking para NR7:{:+6.4f}'.format(PTodoTe[1]))

if PTodoTe[0] > PTodoTe[1]:
    print('El modelo SÍ es coherente con RN6 >~ RN7 ya que Model(RN6)={:+6.4f} > Model(RN7)={:+6.4f}'
          .format(PTodoTe[0],PTodoTe[1]))
else:    
    print('El modelo NO es coherente con RN6 >~ RN7 ya que Model(RN6)={:+6.4f} < Model(RN7)={:+6.4f}'
          .format(PTodoTe[0],PTodoTe[1]))

#<TODO END Ejercicio 1>


