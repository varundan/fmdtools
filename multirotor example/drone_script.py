# -*- coding: utf-8 -*-
"""
File name: quad_script.py
Author: Daniel Hulse
Created: June 2019
Description: I/O with the quadrotor model defined in quad_mdl.py
"""
import sys
sys.path.append('../')

import fmdtools.faultsim.propagate as propagate
import fmdtools.resultdisp as rd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from drone_mdl import *
import time

#scenlist=fp.listinitfaults(graph, mdl.times)


#app = SampleApproach(mdl)
#endclasses, mdlhists = fp.run_approach(mdl, app)
#simplefmea = rp.make_simplefmea(endclasses)
#summfmea = rp.make_summfmea(endclasses, app)
# =============================================================================
params={'start': [0.0,0.0, 10, 10], 'target': [0, 150, 160, 160], 'safe': [0, 50, 10, 10], # areas
        'loc':'rural', # location of use
        'flightplan':{ 1:[0,0,50], 2:[100, 200, 50], 3:[100, 100, 85], 4:[-25, 150, 20],5:[75, 300, 20],6:[0, 300, 20], 7:[0,0,50], 8:[0,0,0] },
        'bat':'series-split',                           #'monolithic', 'series-split', 'paralel-split', 'split-both'
        'linearch':'quad',                              #quad, hex, oct
        'respolicy':{'bat':'emland','line':'emland'}}   #continue, to_home, to_nearest, emland
mdl = Drone(params=params)
endresults_nom, resgraph, mdlhist =propagate.nominal(mdl)
rd.graph.show(resgraph, pos=mdl.graph_pos) #, showfaultlabels=False)
#fp.plotflowhist(flowhist3, 'N/A', time=0)
## 

#params={'flightplan':{ 1:[0,0,50], 2:[100, 0, 50], 3:[100, 100, 50], 4:[150, 150, 50], 5:[0,0,50], 6:[0,0,0] }}
mdl = Drone(params=params)
## #Check various scenarios individually
## 
endresults, resgraph, mdlhist = propagate.one_fault(mdl, 'StoreEE', 'S1P1nocharge', time=5, staged=True, gtype='bipartite')

rd.graph.show(resgraph,gtype='bipartite', pos=mdl.bipartite_pos, faultscen='StoreEE S1P1nocharge', time=5, showfaultlabels=False)
### 
#rp.plot_mdlhistvals(mdlhist, 'DistEE short', time=20) #, fxnflows=['StoreEE'])
rd.plot.mdlhistvals(mdlhist,'StoreEE S1P1nocharge', fxnflowvals={'Planpath':['dx','dy','dz']}, time=5)

rd.plot.mdlhistvals(mdlhist,'StoreEE S1P1nocharge', fxnflowvals={'Force_GR':['value'],'Force_LG':['value'],'Force_ST':['support'],'Force_Lin':['support']}, time=5)

rd.plot.mdlhistvals(mdlhist,'StoreEE S1P1nocharge', time=5)

# mdlhist['nominal']['functions']['Planpath']
### 
#endresults, resgraph, mdlhist2=fp.run_one_fault(mdl, 'AffectDOF', 'RFshort', time=13, staged=True)
# is the model not being reset???

#rp.show_graph(resgraph)
#fp.plotflowhist(flowhist2, 'RFshort', time=13)
#fp.plotghist(ghist2, 't=13 RFshort')
#
xnom=mdlhist['nominal']['flows']['DOFs']['x']
ynom=mdlhist['nominal']['flows']['DOFs']['y']
znom=mdlhist['nominal']['flows']['DOFs']['elev']
#
x=mdlhist['faulty']['flows']['DOFs']['x']
y=mdlhist['faulty']['flows']['DOFs']['y']
z=mdlhist['faulty']['flows']['DOFs']['elev']

time = mdlhist['nominal']['time']


fig2 = plt.figure()

ax2 = fig2.add_subplot(111, projection='3d')
ax2.set_xlim3d(-50, 200)
ax2.set_ylim3d(-50,200)
ax2.set_zlim3d(0,100)
ax2.plot(xnom,ynom,znom)
ax2.plot(x,y,z)

for xx,yy,zz,tt in zip(xnom,ynom,znom,time):
    if tt%20==0:
        ax2.text(xx,yy,zz, 't='+str(tt), fontsize=8)

for goal,loc in params['flightplan'].items():
    ax2.text(loc[0],loc[1],loc[2], str(goal), fontweight='bold', fontsize=12)
    ax2.plot([loc[0]],[loc[1]],[loc[2]], marker='o', markersize=10, color='red', alpha=0.5)

ax2.set_title('Fault response to RFpropbreak fault at t=20')
ax2.legend(['Nominal Flightpath','Faulty Flighpath'], loc=4)
#
plt.show()


plt.figure()
plt.plot(x,y)
plt.plot(xnom,ynom)


xviewed = [x for (x,y),view in endresults_nom['classification']['viewed'].items() if view!='unviewed']
yviewed = [y for (x,y),view in endresults_nom['classification']['viewed'].items() if view!='unviewed']
xunviewed = [x for (x,y),view in endresults_nom['classification']['viewed'].items() if view=='unviewed']
yunviewed = [y for (x,y),view in endresults_nom['classification']['viewed'].items() if view=='unviewed']

plt.scatter(xviewed,yviewed, color='red')
plt.scatter(xunviewed,yunviewed, color='grey')

plt.fill([x[0] for x in mdl.start_area],[x[1] for x in mdl.start_area], color='blue')
plt.fill([x[0] for x in mdl.target_area],[x[1] for x in mdl.target_area], alpha=0.2, color='red')
plt.fill([x[0] for x in mdl.safe_area],[x[1] for x in mdl.safe_area], color='yellow')


plt.show()


app = SampleApproach(mdl, faults='single-component')
a, b = propagate.approach(mdl, app)

p_hazardous = np.sum([v['severities']['hazardous'] for k,v in a.items()])
p_minor = np.sum([v['severities']['minor'] for k,v in a.items()])


#resultstab=fp.runlist(mdl,staged=True)

#resultstab.write('tab4.ecsv', overwrite=True)


#resultstab=fp.run_list(mdl, staged=True)

#t1=time.time()
#endclasses, mdlhists=fp.run_list(mdl, staged=True)
#simplefmea = rp.make_simplefmea(endclasses)
#t2=time.time()
#print(simplefmea)
#reshists, diffs, summaries = rp.compare_hists(mdlhists, returndiff=False)

#t3=time.time()
#t_running = t2-t1
#t_processing =t3-t2
#fullfmea = rp.make_fullfmea(endclasses, summaries)
#heatmap = rp.make_avgdegtimeheatmap(reshists)

#rp.show_bipartite(mdl.bipartite, heatmap=heatmap, scale=2)

#heatmap2 = rp.make_expdegtimeheatmap(reshists, endclasses)
#rp.show_bipartite(mdl.bipartite, heatmap=heatmap2, scale=2)




#print(t_reused)
#print(t_copied)
# based on this test, it appears reusing the model is actually slightly slower
# than copying. Not sure why. However, it's probably the case that execution is
# probably the biggest bottleneck
