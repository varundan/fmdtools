"""
File Name: resultdisp/plot.py
Author: Daniel Hulse
Created: November 2019 (Refactored April 2020)

Description: Plots quantities of interest over time using matplotlib.

Uses the following methods:
    - mdlhist:         plots function and flow histories over time (with different plots for each funciton/flow)
    - mdlhistvals:     plots function and flow histories over time on a single plot 
    - samplecost:      plots the costs for a single fault sampled by a SampleApproach over time with rates
    - samplecosts:     plots the costs for a set of faults sampled by a SampleApproach over time with rates on separate plots
    - costovertime:    plots the total cost/explected cost of a set of faults sampled by a SampleApproach over time
"""
import matplotlib.pyplot as plt
import copy
import numpy as np
from fmdtools.resultdisp.tabulate import costovertime as cost_table

def mdlhist(mdlhist, fault='', time=0, fxnflows=[], returnfigs=False, legend=True, timelabel='Time', units=[]):
    """
    Plots the states of a model over time given a history.

    Parameters
    ----------
    mdlhist : dict
        History of states over time. Can be just the scenario states or a dict of scenario states and nominal states per {'nominal':nomhist,'faulty':mdlhist}
    fault : str, optional
        Name of the fault (for the title). The default is ''.
    time : float, optional
        Time of fault injection. The default is 0.
    fxnflows : list, optional
        List of functions and flows to plot. The default is [], which returns all.
    returnfigs: bool, optional
        Whether to return the figure objects in a list. The default is False.
    legend: bool, optional
        Whether the plot should have a legend for faulty and nominal states. The default is true
    """
    mdlhists={}
    if 'nominal' not in mdlhist: mdlhists['nominal']=mdlhist
    else: mdlhists=mdlhist
    times = mdlhists["nominal"]["time"]
    unitdict = dict(enumerate(units))
    z=0
    figs =[]
    for objtype in ["flows", "functions"]:
        for fxnflow in mdlhists['nominal'][objtype]:
            if fxnflows: #if in the list 
                if fxnflow not in fxnflows: continue
            
            if objtype =="flows":
                nomhist=mdlhists['nominal']["flows"][fxnflow]
                if 'faulty' in mdlhists: hist = mdlhists['faulty']["flows"][fxnflow]
            elif objtype=="functions":
                nomhist=copy.deepcopy(mdlhists['nominal']["functions"][fxnflow])
                del nomhist['faults']
                if 'faulty' in mdlhists: 
                    hist = copy.deepcopy(mdlhists['faulty']["functions"][fxnflow])
                    del hist['faults']
            plots=len(nomhist)
            if plots:
                fig = plt.figure()
                figs = figs +[fig]
                if legend: fig.add_subplot(np.ceil((plots+1)/2),2,plots)
                else: fig.add_subplot(np.ceil((plots)/2),2,plots)
                
                plt.tight_layout(pad=2.5, w_pad=2.5, h_pad=2.5, rect=[0, 0.03, 1, 0.95])
                n=1
                for var in nomhist:
                    plt.subplot(np.ceil((plots+1)/2),2,n, label=fxnflow+var)
                    n+=1
                    if 'faulty' in mdlhists:
                        a, = plt.plot(times, hist[var], color='r')
                        c = plt.axvline(x=time, color='k')
                        b, =plt.plot(times, nomhist[var], ls='--', color='b')
                    else:
                        b, =plt.plot(times, nomhist[var], color='b')
                    plt.title(var)
                    plt.xlabel(timelabel)
                    plt.ylabel(unitdict.get(z, ''))
                    z+=1
                if 'faulty' in mdlhists:
                    fig.suptitle('Dynamic Response of '+fxnflow+' to fault'+' '+fault)
                    if legend:
                        ax_l = plt.subplot(np.ceil((plots+1)/2),2,n, label=fxnflow+'legend')
                        plt.legend([a,b],['faulty', 'nominal'], loc='center')
                        plt.box(on=None)
                        ax_l.get_xaxis().set_visible(False)
                        ax_l.get_yaxis().set_visible(False)
                plt.show()
    if returnfigs: return figs

def mdlhistvals(mdlhist, fault='', time=0, fxnflowvals={}, cols=2, returnfig=False, legend=True, timelabel="time", units=[]):
    """
    Plots the states of a model over time given a history.

    Parameters
    ----------
    mdlhist : dict
        History of states over time. Can be just the scenario states or a dict of scenario states and nominal states per {'nominal':nomhist,'faulty':mdlhist}
    fault : str, optional
        Name of the fault (for the title). The default is ''.
    time : float, optional
        Time of fault injection. The default is 0.
    fxnflowsvals : dict, optional
        dict of flow values to plot with structure {fxnflow:[vals]}. The default is {}, which returns all.
    cols: int, optional
        columns to use in the figure. The default is 2.
    returnfig: bool, optional
        Whether to return the figure. The default is False.
    legend: bool, optional
        Whether the plot should have a legend for faulty and nominal states. The default is true
        
    """
    mdlhists={}
    if 'nominal' not in mdlhist: mdlhists['nominal']=mdlhist
    else: mdlhists=mdlhist
    times = mdlhists["nominal"]["time"]
    
    unitdict = dict(enumerate(units))
    
    if fxnflowvals: num_plots = sum([len(val) for k,val in fxnflowvals.items()])
    else: num_plots = sum([len(flow) for flow in mdlhists['nominal']['flows'].values()])+sum([len(f.keys())-1 for f in mdlhists['nominal']['functions'].values()])
    fig = plt.figure(figsize=(cols*3, 2*num_plots/cols))
    n=1
    
    for objtype in ["flows", "functions"]:
        for fxnflow in mdlhists['nominal'][objtype]:
            if fxnflowvals: #if in the list 
                if fxnflow not in fxnflowvals: continue
            
            if objtype =="flows":
                nomhist=mdlhists['nominal']["flows"][fxnflow]
                if 'faulty' in mdlhists: hist = mdlhists['faulty']["flows"][fxnflow]
            elif objtype=="functions":
                nomhist=copy.deepcopy(mdlhists['nominal']["functions"][fxnflow])
                del nomhist['faults']
                if 'faulty' in mdlhists: 
                    hist = copy.deepcopy(mdlhists['faulty']["functions"][fxnflow])
                    del hist['faults']

            for var in nomhist:
                if fxnflowvals: #if in the list of values
                    if var not in fxnflowvals[fxnflow]: continue
                if legend: plt.subplot(np.ceil((num_plots+1)/cols),cols,n, label=fxnflow+var)
                else: plt.subplot(np.ceil((num_plots)/cols),cols,n, label=fxnflow+var)
                n+=1
                if 'faulty' in mdlhists:
                    a, = plt.plot(times, hist[var], color='r')
                    c = plt.axvline(x=time, color='k')
                    b, =plt.plot(times, nomhist[var], ls='--', color='b')
                else:
                    b, =plt.plot(times, nomhist[var], color='b')
                plt.title(fxnflow+": "+var)
                plt.xlabel(timelabel)
                plt.ylabel(unitdict.get(n-2, ''))
    if 'faulty' in mdlhists:
        if fxnflowvals: fig.suptitle('Dynamic Response of '+str(list(fxnflowvals.keys()))+' to fault'+' '+fault)
        else:           fig.suptitle('Dynamic Response of Model States to fault'+' '+fault)
        if legend:
            ax_l = plt.subplot(np.ceil((num_plots+1)/cols),cols,n, label=fxnflow+'legend')
            plt.legend([a,b],['faulty', 'nominal'], loc='center')
            plt.box(on=None)
            ax_l.get_xaxis().set_visible(False)
            ax_l.get_yaxis().set_visible(False)
    plt.tight_layout(pad=1)
    plt.subplots_adjust(top=1-0.05-0.15/(num_plots/cols))
    if returnfig: return fig
    else: plt.show()

def samplecost(app, endclasses, fxnmode, samptype='std', title=""):
    """
    Plots the sample cost and rate of a given fault over the injection times defined in the app sampleapproach

    Parameters
    ----------
    app : sampleapproach
        Sample approach defining the underlying samples to take and probability model of the list of scenarios.
    endclasses : dict
        A dict with the end classification of each fault (costs, etc)
    fxnmode : tuple
        tuple (or tuple of tuples) with structure ('function name', 'mode name') defining the fault mode
    samptype : str, optional
        The type of sample approach used:
            - 'std' for a single point for each interval
            - 'quadrature' for a set of points with weights defined by a quadrature
            - 'pruned piecewise-linear' for a set of points with weights defined by a pruned approach (from app.prune_scenarios())
            - 'fullint' for the full integral (sampling every possible time)
    """
    associated_scens=[]
    for phase in app.phases:
        associated_scens = associated_scens + app.scenids.get((fxnmode, phase), [])
    costs = np.array([endclasses[scen]['cost'] for scen in associated_scens])
    times = np.array([time  for phase, timemodes in app.sampletimes.items() if timemodes for time in timemodes if fxnmode in timemodes.get(time)] )  
    rates = np.array(list(app.rates_timeless[fxnmode].values()))
    
    tPlot, axes = plt.subplots(2, 1, sharey=False, gridspec_kw={'height_ratios': [3, 1]})
    phasetimes_start =[times[0] for phase, times in app.phases.items()]
    phasetimes_end =[times[1] for phase, times in app.phases.items()]
    ratetimes =[]
    ratesvect =[]
    phaselocs = []
    for (ind, phasetime) in enumerate(phasetimes_start):
        axes[0].axvline(phasetime, color="black")        
        phaselocs= phaselocs +[(phasetimes_end[ind]-phasetimes_start[ind])/2 + phasetimes_start[ind]]

        axes[1].axvline(phasetime, color="black") 
        ratetimes = ratetimes + [phasetimes_start[ind]] + [phasetimes_end[ind]]
        ratesvect = ratesvect + [rates[ind]] + [rates[ind]]
        #axes[1].text(middletime, 0.5*max(rates),  list(app.phases.keys())[ind], ha='center', backgroundcolor="white")
    #rate plots
    axes[1].set_xticks(phaselocs)
    axes[1].set_xticklabels(list(app.phases.keys()))
    
    axes[1].plot(ratetimes, ratesvect)
    axes[1].set_xlim(phasetimes_start[0], phasetimes_end[-1])
    axes[1].set_ylim(0, np.max(ratesvect)*1.2 )
    axes[1].set_ylabel("Rate")
    axes[1].set_xlabel("Time ("+str(app.units)+")")
    axes[1].grid()
    #cost plots
    axes[0].set_xlim(phasetimes_start[0], phasetimes_end[-1])
    axes[0].set_ylim(0, 1.2*np.max(costs))
    if samptype=='fullint':
        axes[0].plot(times, costs, label="cost")
    else:
        if samptype=='quadrature' or samptype=='pruned piecewise-linear': 
            sizes =  1000*np.array([weight if weight !=1/len(timeweights) else 0.0 for phase, timeweights in app.weights[fxnmode].items() for time, weight in timeweights.items() if time in times])
            axes[0].scatter(times, costs,s=sizes, label="cost", alpha=0.5)
        axes[0].stem(times, costs, label="cost", markerfmt=",", use_line_collection=True)
    
    axes[0].set_ylabel("Cost")
    axes[0].grid()
    if title: axes[0].set_title(title)
    elif type(fxnmode[0])==tuple: axes[0].set_title("Cost function of "+str(fxnmode)+" over time")
    else:                       axes[0].set_title("Cost function of "+fxnmode[0]+": "+fxnmode[1]+" over time")
    #plt.subplot_adjust()
    plt.tight_layout()
def samplecosts(app, endclasses, joint=False, title=""):
    """
    Plots the costs and rates of a set of faults injected over time according to the approach app

    Parameters
    ----------
    app : sampleapproach
        The sample approach used to run the list of faults
    endclasses : dict
        A dict of results for each of the scenarios.
    joint : bool, optional
        Whether to include joint fault scenarios. The default is False.
    """
    for fxnmode in app.list_modes(joint):
        if any([True for (fm, phase), val in app.sampparams.items() if val['samp']=='fullint' and fm==fxnmode]):
            st='fullint'
        elif any([True for (fm, phase), val in app.sampparams.items() if val['samp']=='quadrature' and fm==fxnmode]):
            st='quadrature'
        else: 
            st='std'
        samplecost(app, endclasses, fxnmode, samptype=st, title="")

def costovertime(endclasses, app, costtype='expected cost'):
    """
    Plots the total cost or total expected cost of faults over time.

    Parameters
    ----------
    endclasses : dict
        dict with rate,cost, and expected cost for each injected scenario (e.g. from run_approach())
    app : sampleapproach
        sample approach used to generate the list of scenarios
    costtype : str, optional
        type of cost to plot ('cost', 'expected cost' or 'rate'). The default is 'expected cost'.
    """
    costovertime = cost_table(endclasses, app)
    plt.plot(list(costovertime.index), costovertime[costtype])
    plt.title('Total '+costtype+' of all faults over time.')
    plt.ylabel(costtype)
    plt.xlabel("Time ("+str(app.units)+")")
    plt.grid()


