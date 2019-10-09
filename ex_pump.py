# -*- coding: utf-8 -*-
"""
File name: ex_pump.py
Author: Daniel Hulse
Created: October 2019
Description: A simple model for explaining fault model definition

This model constitudes an extremely simple functional model of an electric-powered pump.

The functions are:
    -import EE
    -import Water
    -import Signal
    -move Water
    -export Water

The flows are:
    - EE (to power the pump)
    - Water_in
    - Water_out
    - Signal input (on/off)
"""


import networkx as nx
import numpy as np

import faultprop as fp
from modeldef import *

#Declare time range to run model over
times=[0,3, 55]


##DEFINE MODEL FUNCTIONS
# Functions are, again, defined using Python classes that are instantiated as objects

# Import EE is the line of electricity going into the pump
# We define it here as a subclass of the fxnblock superclass (imported from modeldef.py)
#the fxnblock superclass, which adds the common aspects of the function objects:
# - flows added to .flow
# - faults set to nominal
# - a number of useful methods added for dealing with internal faults (e.g. addfault()) and fault
# propagation (e.g. updatefxn()) are added to the object
class importEE(fxnblock):
    #Initializing the function requires the flows going in and out of the function
    def __init__(self,EEout):
        #this initializes the fault state of the system and adds needed flows
        #self.faults will be used to store which faults are in the function
        #flows will now be attibutes with names given by the keys in the input
        # dict, e.g. {'EEout':EEout} means self.EEout will be the EEout flow
        super().__init__({'EEout':EEout})

        #fault modes that originate in the function are listed here in a dictionary
        #these modes will be used to generate a list of scenarios
        #each fault can be given arbitrary properties in a dictionary
        #in this case, rate and repair cost information
        self.faultmodes={'no_v':{'rate':'moderate', 'rcost':'major'}, \
                         'inf_v':{'rate':'rare', 'rcost':'major'}}
        
    #condfaults changes the state of the system if there is a change in state in a flow
    # using a condfaults method is optional but helpful for delinating between
    # the determination of a fault and the behavior that results
    def condfaults(self,time):
        #in this case, if the current is too high, the line becomes an open circuit
        # (e.g. due to a fuse or line burnout)
        if self.EEout.rate>5.0: self.addfault('no_v')
    #behavior defines the behavior of the function
    def behavior(self,time):
        #here we can define how the function will behave with different faults
        if self.hasfault('no_v'): self.EEout.effort=0.0 #an open circuit means no voltage is exported
        elif self.hasfault('inf_v'): self.effstate=100.0 #a voltage spike means voltage is much higher
        else: self.effstate=1.0 #normally, voltage is 1.0

# Import Water is the pipe with water going into the pump

class importWater(fxnblock):
    #Initializing the function requires the flows going in and out of the function
    def __init__(self,Watout):
        #init requires a dictionary of flows with the internal variable name and
        # the object reference
        super().__init__({'Watout':Watout})
        self.faultmodes={'no_wat':{'rate':'moderate', 'rcost':'major'}}
    #in this function, no conditional faults are modelled, so we don't need to include it
    #a dummy version is used in the fxnblock superclass
    def behavior(self,time):
        #here we can define how the function will behave with different faults
        if self.hasfault('no_wat'):
            self.Watout.level=0.0 #an open circuit means no voltage is exported
        else:
            self.Watout.level=1.0

# Import Water is the pipe with water going into the pump
class exportWater(fxnblock):
    #Initializing the function requires the flows going in and out of the function
    def __init__(self,Watin):
        #flows going into/out of the function need to be made properties of the function
        super().__init__({'Watin':Watin})
        self.faultmodes={'block':{'rate':'moderate', 'rcost':'major'}}
    def behavior(self,time):
        if self.hasfault('block'): #here the fault is some sort of blockage
            self.Watin.area=0.1

# Import Signal is the on/off switch
class importSig(fxnblock):
    def __init__(self,Sigout):
        #flows going into/out of the function need to be made properties of the function
        super().__init__({'Sigout':Sigout})
        self.faultmodes={'no_sig':{'rate':'moderate', 'rcost':'major'}}
    #when the behavior changes over time (and not just internal state) time must
    # be given as an input
    def behavior(self, time):
        if self.hasfault('no_sig'):
            self.Sigout.power=0.0 #an open circuit means no voltage is exported
        else:
            #Since the signal *generally* defines the operational profile of the system,
            # here we can specify what the system is supposed to do over time
            # in this case, turning on and then off
            if time<5:
                self.Sigout.power=0.0
            elif time<50:
                self.Sigout.power=1.0
            else:
                self.Sigout.power=0.0

# Move Water is the pump itself. While one could decompose this further,
# one function is used for simplicity
class moveWat(fxnblock):
    def __init__(self,EEin, Sigin, Watin, Watout):
        flows={'EEin':EEin, 'Sigin':Sigin, 'Watin':Watin, 'Watout':Watout}
        #here we also define the states of a model, which are also added as 
        #attributes to the function
        states={'eff':1.0} #effectiveness state
        super().__init__(flows,states)
        self.faultmodes={'mech_break':{'rate':'moderate', 'rcost':'major'}, \
                         'short':{'rate':'rare', 'rcost':'major'}}
        #timers can be set by adding variables to functions also
        self.t1=0.0
        self.t2=0.0
        self.timer=0.0
    def condfaults(self, time):
        # here we define a conditional fault that only occurs after a state 
        # is present after 10 seconds
        if self.Watout.effort>5.0:
            if self.t1>time:
                self.t1=time
                self.timer+=1
            if self.timer>10.0:
                self.addfault('mech_break')
    #behavior defines the behavior of the function
    def behavior(self, time):
        #here we can define how the function will behave with different faults
        if self.hasfault('mech_break'):
            self.EEin.rate=0.1*self.Sigin.power*self.EEin.effort
            self.eff=0.0
        if self.hasfault('short'):
            self.EEin.rate=500*self.Sigin.power*self.EEin.effort
            self.eff=0.0
        else:
            self.EEin.rate=1.0*self.Sigin.power*self.EEin.effort
            self.eff=1.0 
            
        self.Watout.effort=self.Sigin.power*self.eff*self.Watin.level/self.Watout.area
        self.Watout.rate=self.Sigin.power*self.eff*self.Watin.level*self.Watout.area
        
        self.Watin.effort=self.Watout.effort
        self.Watin.rate=self.Watout.rate

##DEFINE CUSTOM MODEL FLOWS
# Flows can be defined using Python classes that are instantiated as objects
# Most flows are defined in the initialize() function, however custom flows can
# also be defined here as needed
    
# Defining the class for the flow of Water
# here the flow is given the custom attribute of 'hello'--further attributes
# and methods could be given here if desired.
class Water(flow):
    def __init__(self):
        attributes={'rate':1.0, \
                    'effort':1.0, \
                    'area':1.0, \
                    'level':1.0}
        super().__init__(attributes, 'Water')
        self.customattribute='hello'
    
#INSTANTIATE MODEL
#the model is initialized using an initialize function
def initialize():
    #INITIALIZE FUNCTION AND FLOW OBJECTS
    
    
    #Flows must be instantiated prior to the functions that use them, since
    # the functions take them as input
    #As shown below, flows are often simple enough that they don't need to be defined
    #as classes at all, but can instead be instantiated directly from the flow class
    EE_1=flow({'rate':1.0, 'effort':1.0}, 'EE')
    Sig_1=flow({'power':1.0}, 'Signal')
    
    #Here we instantiate the custom flows defined 
    Wat_1=Water()
    Wat_2=Water()
    
    
    #function objects take their respective flows as input 
    Imp_EE=importEE(EE_1)
    Imp_Wat=importWater(Wat_1)
    Imp_Sig=importSig(Sig_1)
    Move_Wat=moveWat(EE_1, Sig_1, Wat_1, Wat_2)
    Exp_Wat=exportWater(Wat_2)
    
    #INITIALIZE AND ASSOCIATE OBJECTS WITH GRAPH
    #initializing the graph
    g=nx.DiGraph()
    
    #add nodes. The first argument gives the node a name. 
    #obj=fxn gives the graph structure the object instantiated for the function
    g.add_node('Import EE', obj=Imp_EE)
    g.add_node('Import Water', obj=Imp_Wat)
    g.add_node('Import Signal', obj=Imp_Sig)
    g.add_node('Move Water', obj=Move_Wat)
    g.add_node('Export Water', obj=Exp_Wat)
    
    #connect the notes with edges
    # flow_1=flow_1 associates a given flow with the edge
    #note that multiple flows can be added to edges using 
    #flow_1=flow_1, flow_2=flow_2 ... etc
    g.add_edge('Import EE', 'Move Water', EE_1=EE_1)
    g.add_edge('Import Signal', 'Move Water', Sig_1=Sig_1)
    g.add_edge('Import Water', 'Move Water', Wat_1=Wat_1)
    g.add_edge('Move Water', 'Export Water', Wat_2=Wat_2)
    
    return g

#PROVIDE MEANS OF CLASSIFYING RESULTS
# this function classifies the faults into severities based on the state of faults
# in this case, we will just use the repair costs and the probability
def findclassification(resgraph, endfaults, endflows, scen):
    
    #get fault costs and rates
    repcosts=fp.listfaultsprops(endfaults, resgraph, 'rcost')
    costs=repcosts.values()
    costkey={'major': 10000, 'minor': 1000}
    totcost=0.0
    
    for cost in costs:
        totcost=totcost+costkey[cost]
    
    life=100
    
    if scen['properties']['type']=='nominal':
        rate=1.0
    else:
        qualrate=scen['properties']['rate']
        ratekey={'rare': 1e-7, 'moderate': 1e-5}
        rate=ratekey[qualrate]
    
    life=1e5
    
    expcost=rate*life*totcost
    
    return {'rate':rate, 'cost': totcost, 'expected cost': expcost}
    