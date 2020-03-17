# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 03:26:48 2020

@author: zhang
"""
from scipy.optimize import differential_evolution
import sys
sys.path.append('../')
import pandas as pd
import fmdtools.faultprop as fp
import fmdtools.resultproc as rp
import csv
import time
import numpy as np
from fmd_final_version import *
#from disease_model import *

#x0 = np.array([0.11 , 1 , 5 , 9.27 , 0.05 , 10 ])
x0 = [0.1 , 2 , 5 , 10 , 0.05 , 10 ]
dm1 = DiseaseModel(x0)
    
rp.show_graph(dm1.graph)

endresults, resgraph, mdlhist_nom = fp.run_nominal(dm1)

rp.plot_mdlhist(mdlhist_nom, fxnflows=['Campus'])

normal_state_table = rp.make_histtable(mdlhist_nom)
normal_state_table.to_csv('normal_state_table.csv')


    
#bounds = [(0, 0.2), (1, 10),(1, 5),(9, 11),(0, 0.2),(0, 10)]
#result = differential_evolution(DiseaseModel, bounds, maxiter=10000)

#def cost(x):
#    x0 = np.array([x[0],x[1],x[2],x[3],x[4],x[5]])
#    dm1 = DiseaseModel(x0)
#    endresults, resgraph, mdlhist_pl1 = fp.run_nominal(dm1)
#    XXX= endresults['classification']['total cost']
#    
#    return XXX
#    
#    
#bounds = [(0, 0.2), (1, 5),(1, 5),(9, 11),(0, 0.2),(0, 5)] 
#result = differential_evolution(cost, bounds, maxiter=100)
#
#print(result.x)
#print(result.fun)

