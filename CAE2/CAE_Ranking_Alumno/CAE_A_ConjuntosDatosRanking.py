# -*- coding: utf-8 -*-
"""
Sesión 2 : Ranking
Bloque A : Conjunto de datos de ranking
"""

# 
# Los conjuntos de datos de ranking están formados por lotes.
# Cada lote tiene varios ejemplos con un valor numérico cada uno
# El valor numérico (suele ser un entero) solo sirve para establecer preferencias
#entre los ejemplos, de manera que dados dos ejemplos, si el ejemplo A tiene un valor
#numérico mayor el ejemplo B, esto indica que se prefiere el A al B.
# Si el valor numérico es el mismo, no hay indicación de preferencia entre ellos.
# Estas preferencias solo son aplicables dentro de un bloque, nunca se pueden
#establecer preferencias entre ejemplos de diferentes bloques.
# En esta práctica se indicará que un ejemplo A se prefiere a otro B de la 
#siguiente manera: A>~B. Si no se establecen preferencias se indica A=~B.

# La estructura de datos propuesta para guardar la información anterior consiste
#en que la categoría de cada ejemplo sea una lista con dos valores: 
#Y=[[RankVal1,Lote1],[RankVal2,Lote2],...]
# Donde RankVal es el valor de ranking, el que se compara para establecer preferencias
#y Lote es el identificador del lote (generalmente un entero)

#Cuando hay un solo lote la categoría puede ser una lista de RankVal

# Ejemplo 1. Un lote
# En una competicción de robots se ha logrado la siguiente clasificación:
# R1 > ~R3 >~ R4 >~ R2
#Donde cada robot está definido como:
# R1 : [1, 34]
# R2 : [3, 25]
# R3 : [2, 14]
# R4 : [2, 45]
# Crear la estructura de datos que almacene la información de esas preferencias

# Robots:
R1=[1, 34]
R2=[3, 25]
R3=[2, 14]
R4=[2, 45]

# Orden (solo un lote)
X=[R1,R3,R4,R2]
Y=[4 ,3 ,2 ,1 ]

# Ejemplo 2. Varios Lotes
# Hay varios críticos que han realizado las siguientes preferencias de restaurantes:
#  R2 >~ R1, 
#  R2 >~ R4 =~ R3 >~ R1
#  R2 >~ R3 >~ R4 >~ R1
# Los atributos que definen cada restaurante son:
# R1 : [9.4, 5.0]
# R2 : [0.5, -1]
# R3 : [3.5, 0]
# R4 : [7.5, 2.3]
# Crear la estructura de datos que almacene la información de esas preferencias

# Restaurantes
R1=[9.4,  5.0]
R2=[0.5, -1]
R3=[3.5,  0]
R4=[7.5,  2.3]

X=[R2    ,R1    ,R2    ,R4    ,R3    ,R1    ,R2    ,R3    ,R4    ,R1]
Y=[[2,1] ,[1,1] ,[3,2] ,[2,2] ,[2,2] ,[1,2] ,[4,3] ,[3,3] ,[2,3] ,[1,3]]

# Ejercicio 1
# En un laboratorio de pruebas se hacen pruebas a muestras de acero. 
# Las muestras de aceros vienen determinadas por la composición química siguiente:
# A1 : Fe=99.50%, C=0.5%  A1=[99.50,0.5]
# A2 : Fe=98%   , C=0.5%, Cd=1.5%
# A3 : Fe=99%   , Cd=1%
# Se han realizado tres pruebas:
# P1 : A1 >~ A2 
# P2 : A2 >~ A1 >~ A3
# P3 : A1 >~ A3


# Crear la estructura de datos que almacene la información de esas preferencias

#<TODO BEGIN Ejerccio 1>
A1=[99.50,0.5,0]
A2=[98   ,0.5,1.5]
A3=[99   ,0  ,1]

X=[A1    ,A2    ,A2    ,A1    ,A3    ,A1    ,A3]
Y=[[2,1] ,[1,1] ,[3,2] ,[2,2] ,[1,2] ,[2,3] ,[1,3]]

#<TODO END Ejerccio 1>
