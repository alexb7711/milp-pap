# Standard Lib
import gurobipy as gp
import numpy as np
import yaml
import random

from gurobipy import GRB
from yaml import Loader

# Developed
from array_util import *

##===============================================================================
#
class YAMLSchedule:

    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   file  : Path to the yaml file
    #   model : Gurobi model
    #
    def __init__(self, f, model):
        stream    = open(f, 'r')
        self.data = yaml.load(stream, Loader=Loader)

        self.model = model
        return

    ##---------------------------------------------------------------------------
    # Input:
    #
    # Output:
    #   Schedule: The loaded schedule from yaml file
    #
    def generate(self):
        # A
        self.__countBuses()

        # N
        self.__countVisits()

        # Q
        self.__countChargers()

        # a
        self.__genArivals()

        # H_min
        self.__getMinCharge()

        # alpha
        self.__getInitCharge()

        # beta
        self.__getFinalCharge()

        # Bus Capacities
        self.__getCapacities()

        # lambda
        self.__calcPowerLoss()

        # r
        self.__getChargeRates()

        # m
        self.__getAssignCosts()

        # e
        self.__getUseCosts()

        # T
        self.__getTimeHorizon()

        # Group Data
        self.__groupData()

        # t
        self.__genDepartureTimes()

        # Gamma
        self.__genBusIdx()

        # gamma
        self.__genNextVisits()

        # a
        self.__genArrivalTimes()

        # final arrivals
        self.__genFinalArrival()

        # Decision Variables
        self.__genDecisionVars()

        schedule = \
        {
            ## Input Variables
            'A'     : self.A,
            'Gamma' : self.Gamma,
            'N'     : self.N,
            'Q'     : self.Q,
            'S'     : 1.0,
            'T'     : self.T,
            'a'     : self.a,
            'alpha' : self.alpha,
            'beta'  : self.beta,       # [%]
            'cap'   : self.capacity,   # [kwh]
            'e'     : self.e,
            'fa'    : self.final_arr,
            'gamma' : self.gamma,
            'l'     : self.l,
            'm'     : self.m,
            'r'     : self.r,
            't'     : self.t,

            ## Decision Variables
            'c'     : self.c,
            'delta' : self.delta,
            'eta'   : self.eta,
            'g'     : self.g,
            'p'     : self.p,
            'sigma' : self.sigma,
            'u'     : self.u,
            'v'     : self.v,
            'w'     : self.w,

            # Model
            'model' : self.model,
        }

        return schedule

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    # Input:
    def __countBuses(self):
        self.A = len([x for x in self.data["buses"]])
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __countVisits(self):
        visit = []

        for i in self.data["buses"]:
            for j in i["route"]["durations"]:
                visit.append(j)

        self.N = len(visit)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __countChargers(self):
        chargers = self.data["chargers"]
        self.Q = chargers["osc"]["num"] + chargers["depot"]["num"]
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __genArivals(self):
        starts = []

        for i in self.data["buses"]:
            starts.append(i["route"]["starts"])

        self.a = np.array(starts, dtype=object)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getMinCharge(self):
        self.H_min = 0.25
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getCapacities(self):
        capacities = []

        for i in self.data["buses"]:
            capacities.append(i["battery"]["capacity"])

        self.capacity = np.array(capacities)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __calcPowerLoss(self):
        l = []

        for i in self.data["buses"]:

            for j in range(len(i["route"]["durations"])):
                duration   = i["route"]["durations"][j]
                motor_load = i["motor_load"]

                l.append(motor_load*duration)

        self.l = np.array(l)
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getChargeRates(self):
        arr = [self.data["chargers"]["osc"]["rate"]]
        cnt = self.data["chargers"]["osc"]["num"]
        osc = np.repeat(arr, cnt)

        arr   = [self.data["chargers"]["depot"]["rate"]]
        cnt   = self.data["chargers"]["depot"]["num"]
        depot = np.repeat(arr, cnt)

        self.r = np.append(depot, osc)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getAssignCosts(self):
        self.m = 2*self.r.copy()
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getUseCosts(self):
        self.e = self.r.copy()
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __genBusIdx(self):
        Gamma = []

        for i in self.gd:
            Gamma.append(i["id"])

        self.Gamma = np.array(Gamma)

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N: Number of visits
    #   Gamma: List of ID's for each visit
    #
    # Output:
    #   gamma: List of index for the next visit
    #
    def __genNextVisits(self):
        # Local Variables
        ## Keep track of the previous index each bus arrived at
        next_idx = np.array([final(self.Gamma, i) for i in range(self.A)], dtype=int)
        gamma    = np.zeros(self.N, dtype=int)

        ## Keep track of the first instance each bus arrives
        last_idx = next_idx.copy()

        # Loop through each bus visit
        for i in range(self.N-1, -1, -1):
            ## Make sure that the index being checked is greater than the first
            ## visit. If it is, set the previous index value equal to the current.
            ## In other words, index i's value indicates the next index the bus
            ## will visit.
            if i < last_idx[self.Gamma[i]]:
                gamma[i]                = next_idx[self.Gamma[i]]
                next_idx[self.Gamma[i]] = i

        self.gamma = np.array(gamma)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getTimeHorizon(self):
        self.T = self.data["sim_duration"]
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __groupData(self):
        group_data = []
        bus       = self.data["buses"]
        iden      = 0

        for i in bus:
            for j in range(len(i["route"]["starts"])):
                start = i["route"]["starts"][j]
                dur   = i["route"]["durations"][j]
                group_data.append({"id": iden, "start": start ,"duration": dur})

            iden += 1

        self.gd = np.array(sorted(group_data, key=lambda k: k["start"]))

        return

    ##---------------------------------------------------------------------------
    # Input:
    #   N     : Number of visits
    #   Gamma : List of ID'ss for each visit
    #
    # Output:
    #   final_arr: List of indices for the final arrival for each bus
    #
    def __genFinalArrival(self):
        self.final_arr = np.ones(self.A, dtype=int)

        for i in range(self.A):
            self.final_arr[i] = final(self.Gamma, i)

    ##---------------------------------------------------------------------------
    # Input:
    def __genDepartureTimes(self):
        t = []

        for i in self.gd:
            t.append(i["start"] + i["duration"])

        self.t = np.array(t)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __genDecisionVars(self):
        # Generate decision variables
        ## Initial charge time
        self.u = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="u")

        ## Assigned queue
        self.v = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="v")

        ## Detatch tiself.model.
        self.c = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="c")

        ## Charge tiself.model.
        self.p = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="p")

        ## Lineriztion term
        self.g = self.model.addMVar(shape=self.N*self.Q, vtype=GRB.CONTINUOUS, name="g")

        ## Initial charge
        self.eta = self.model.addMVar(shape=self.N, vtype=GRB.CONTINUOUS, name="eta")

        ## Vector representation of queue
        self.w = self.model.addMVar(shape=self.N*self.Q, vtype=GRB.BINARY, name="w")

        ## Sigma
        #  sigma = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.BINARY, name="sigma")
        self.sigma = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.CONTINUOUS, name="sigma")

        ## Delta
        #  delta = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.BINARY, name="delta")
        self.delta = self.model.addMVar(shape=self.N*(self.N-1), vtype=GRB.CONTINUOUS, name="delta")

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getInitCharge(self):
        init_charge = []

        for i in self.data["buses"]:
            init_charge.append(i["battery"]["charge"])

        self.alpha = np.array(init_charge)

        return

    ##---------------------------------------------------------------------------
    # Input:
    def __getFinalCharge(self):
        self.beta = 0.95
        return

    ##---------------------------------------------------------------------------
    # Input:
    def __genArrivalTimes(self):
        a = []
        for i in self.gd:
            a.append(i["start"])

        self.a = np.array(a)

        return
