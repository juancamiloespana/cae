#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tema: Cuantificación
Estudiante: Juan Camilo España
Curso: Métodos Basados en el conocimiento aplicado a la empresa (CAE).

Contexto:
Utilizar algoritmos de cuantificación que permita estimar la prevalencia de alucinaciones
en recomendaciones médicas hechas por LLMs como medida de riesgo y de comparación en la
evolución de estos sistemas.

Una empresa consultora de IA analiza las alucinaciones de LLM cuando generan recomendaciones
médicas. Ha realizado dos evaluaciones con expertos usando diferentes versiones de un LLM
propietario. Dado que estos sistemas siguen siendo actualizados, se requiere un algoritmo de
cuantificación para reducir costos en la evaluación e identificar características que aumenten
las alucinaciones.

El tercer dataset se quiere medir utilizando el sistema entrenado con los datasets anteriores.
"""

# =============================================================================
# IMPORTS
# =============================================================================
# import os, sys
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(os.path.abspath(__file__))


from quantificationlib.baselines.cc import CC
from quantificationlib.baselines.ac import AC, PAC
from quantificationlib.multiclass.df import DFX
from quantificationlib.ensembles import eoq
from quantificationlib.bag_generator import PriorShift_BagGenerator
from QUtils import dataSetFromQBags

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

import numpy as np
import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import optuna as opt


from sklearn.metrics import ConfusionMatrixDisplay

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
        for Q in self.QList:
            # B) En pe1 se alm
            self.Qlist[Q].fit()
        

            
        return self
    
    def predict(self,X):
        """
        Predice la prevalencia como la media de las prevalencias de cada sistema
        """
        prevs=[0,0]
        for Q in self.QList:
            # B) En pe1 se almacena la prevalencia de la clase 1 para el cuantificador Q
            pe1=self.QList[Q].predict(self)
         
            
            prevs[0]=prevs[0]+(1-pe1)
            prevs[1]=prevs[1]+pe1
        prevs[0]=prevs[0]/len(self.QList)
        prevs[1]=prevs[1]/len(self.QList)
        
        return prevs
        
        





# =============================================================================
# CARGA DE DATOS
# =============================================================================

DF_E1 = pd.read_csv('datasets/dataset_E1.csv')
DF_E2 = pd.read_csv('datasets/dataset_E2.csv')
DF_E3 = pd.read_csv('datasets/dataset_E3.csv')


print(DF_E1.head());  print(DF_E1.info());  print(DF_E1.describe())
print(DF_E2.head());  print(DF_E2.info());  print(DF_E2.describe())
print(DF_E3.head());  print(DF_E3.info());  print(DF_E3.describe())

X_E1 = DF_E1.drop(columns=['y_alucinacion']).values
Y_E1 = DF_E1['y_alucinacion'].values
X_E2 = DF_E2.drop(columns=['y_alucinacion']).values
Y_E2 = DF_E2['y_alucinacion'].values
X_E3 = DF_E3.drop(columns=['y_alucinacion']).values
Y_E3 = DF_E3['y_alucinacion'].values  # en teoría no existe — solo para verificación final

print(f' Prevalencia en Evaluación 1: {np.mean(Y_E1):.2f}')
print(f' Prevalencia en Evaluación 2: {np.mean(Y_E2):.2f}')


# =============================================================================
# CLASIFICADOR BASE
# =============================================================================

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_E1, Y_E1)

pred_e1 = clf.predict(X_E1)
print(f'Prevalencia predicha en E1 (clasificador): {np.mean(pred_e1):.2f}')
print(classification_report(Y_E1, pred_e1))

pred_e2 = clf.predict(X_E2)
print(f'Prevalencia predicha en E2 (clasificador): {np.mean(pred_e2):.2f}')
# La prevalencia predicha está por debajo de la real de E2 (0.35) — sesgo de dataset shift


ConfusionMatrixDisplay.from_estimator(clf, X_E2, Y_E2)
plt.savefig('figures/confusion_E2.pdf')

# =============================================================================
# ENTRENAMIENTO DE CUANTIFICADORES (CC / AC / PAC / DFX)
# =============================================================================

dict_pre_es = {}



# CC
Q_cc = CC(clf)
Q_cc.fit(X_E1, Y_E1)
Q_cc_pre_es = Q_cc.predict(X_E2)
print(Q_cc.classes_)
dict_pre_es['CC'] = Q_cc_pre_es[np.argwhere(Q_cc.classes_ == 1)[0][0]]

# AC
Q_ac = AC(estimator_train=clf, estimator_test=clf)
Q_ac.fit(X_E1, Y_E1)
Q_ac_pre_es = Q_ac.predict(X_E2)
print(Q_ac.classes_)
dict_pre_es['AC'] = Q_ac_pre_es[np.argwhere(Q_ac.classes_ == 1)[0][0]]




listQs=[Q_ac,Q_cc]
Q_combi = CombiQuanty(clf,listQs)
Q_combi.fit(X_E1, Y_E1)
Q_combi_pre_es = Q_combi.predict(X_E2)
print(Q_combi.classes_)
dict_pre_es['Combi'] = Q_combi_pre_es[np.argwhere(Q_combi.classes_ == 1)[0][0]]




# PAC
Q_pac = PAC(estimator_train=clf, estimator_test=clf)
Q_pac.fit(X_E1, Y_E1)
Q_pac_pre_es = Q_pac.predict(X_E2)
print(Q_pac.classes_)
dict_pre_es['PAC'] = Q_pac_pre_es[np.argwhere(Q_pac.classes_ == 1)[0][0]]

# DFX (multiclass)
Q_dfx = DFX(n_bins=50, distance='L2')
Q_dfx.fit(X_E1, Y_E1)
Q_dfx_pre_es = Q_dfx.predict(X_E2)
print(Q_dfx.classes_)
dict_pre_es['DFX'] = Q_dfx_pre_es[np.argwhere(Q_dfx.classes_ == 1)[0][0]]

df_pre_es = pd.DataFrame.from_dict(dict_pre_es, orient='index', columns=['Prevalencia_E2'])
df_pre_es['Error_Absoluto-L1']   = abs(df_pre_es['Prevalencia_E2'] - np.mean(Y_E2))
df_pre_es['Error_Cuadratico-L2'] = df_pre_es['Error_Absoluto-L1'] ** 2
print(df_pre_es)


# =============================================================================
# VISUALIZACIÓN — PRESELECCIÓN DE CUANTIFICADOR A AFINAR
# =============================================================================

df_pre_es['index'] = df_pre_es.index
scatterplot = sns.scatterplot(
    data=df_pre_es,
    x='Error_Cuadratico-L2',
    y='Error_Absoluto-L1',
    hue='index',
)
plt.title('L1 vs L2')
plt.savefig('figures/scatter_L1_L2.pdf')
plt.show()


# =============================================================================
# AFINAMIENTO DE HIPERPARÁMETROS DE DFX CON OPTUNA
# =============================================================================

def objective(trial):
    n_bins   = trial.suggest_int('n_bins', 10, 200)
    distance = trial.suggest_categorical('distance', ['L1', 'L2', 'HD'])
    q = DFX(n_bins=n_bins, distance=distance)
    q.fit(X_E1, Y_E1)
    pred = q.predict(X_E2)
    prev = pred[np.argwhere(q.classes_ == 1)[0][0]]
    return abs(prev - np.mean(Y_E2))  # minimizar error L1

study = opt.create_study(direction='minimize')
study.optimize(objective, n_trials=200)
print(f"Mejor configuración DFX: {study.best_params}  →  error L1={study.best_value:.4f}")

l1_trials = [t.value for t in study.trials]
best_idx   = int(np.argmin(np.minimum.accumulate(l1_trials)))
plt.figure(figsize=(7, 3))
plt.plot(l1_trials, color='steelblue', linewidth=0.8, label='Error L1 por intento')
plt.plot(np.minimum.accumulate(l1_trials), color='tomato', linewidth=1.5, label='Mejor acumulado')
plt.axvline(best_idx, color='tomato', linestyle='--', linewidth=0.8)
plt.xlabel('Intento'); plt.ylabel('Error L1')
plt.title('Búsqueda de hiperparámetros DFX (Optuna)')
plt.legend(); plt.tight_layout()
plt.savefig('figures/optuna_history.pdf')
plt.show()

n_bins   = study.best_params['n_bins']
distance = study.best_params['distance']


# =============================================================================
# ESTIMACIÓN DE CALIDAD DEL MODELO DFX AFINADO (sobre E2 con bags)
# =============================================================================

Q_dfx_best = DFX(n_bins=n_bins, distance=distance)
Q_dfx_best.fit(X_E1, Y_E1)

n_bags = 200
BG   = PriorShift_BagGenerator(n_bags=n_bags, random_state=1)
bags = BG.generate_bags(X_E2, Y_E2)

l1s = []
print('\nEstimando calidad para DFX (n_bins={}, distance={})'.format(n_bins, distance))
for i in range(n_bags):
    [Xb, Yb] = dataSetFromQBags(X_E2, Y_E2, bags, i)
    p  = np.mean(Yb)
    pe = Q_dfx_best.predict(Xb)[np.argwhere(Q_dfx_best.classes_ == 1)[0][0]]
    l1 = abs(pe - p)
    print('{:3}/{:3} Prevalencia real:{:6.4f}  DFX:{:6.4f}  l1={:6.4f}'.format(i, n_bags - 1, p, pe, l1))
    l1s.append(l1)

print('DFX, l1 medio: {:6.4f}'.format(np.mean(l1s)))

ps  = [np.mean(dataSetFromQBags(X_E2, Y_E2, bags, i)[1]) for i in range(n_bags)]
pes = [Q_dfx_best.predict(dataSetFromQBags(X_E2, Y_E2, bags, i)[0])[np.argwhere(Q_dfx_best.classes_==1)[0][0]] for i in range(n_bags)]
plt.figure(figsize=(5, 5))
plt.scatter(ps, pes, s=10, alpha=0.5, color='steelblue')
plt.plot([0, 1], [0, 1], 'r--', linewidth=1, label='Estimación perfecta')
plt.xlabel('Prevalencia real'); plt.ylabel('Prevalencia estimada')
plt.title('DFX afinado — 200 bags sobre E2')
plt.legend(); plt.tight_layout()
plt.savefig('figures/bags_scatter.pdf')
plt.show()


# =============================================================================
# PRODUCCIÓN — MODELO FINAL Y PREDICCIÓN SOBRE E3
# =============================================================================

# Entrena con E1 + E2 combinados para aprovechar todos los datos etiquetados
X_train_final = np.vstack((X_E1, X_E2))
Y_train_final = np.hstack((Y_E1, Y_E2))

Q_dfx_final = DFX(n_bins=n_bins, distance=distance)
Q_dfx_final.fit(X_train_final, Y_train_final)

prevalencia_E3 = Q_dfx_final.predict(X_E3)[np.argwhere(Q_dfx_final.classes_ == 1)[0][0]]

print('Prevalencia estimada en E3 con DFX afinado: {:6.4f}'.format(prevalencia_E3))
print('Prevalencia real en E3 (no se conoce en producción): {:6.4f}'.format(np.mean(Y_E3)))

# output: prevalencia_E3
