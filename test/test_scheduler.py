#!/usr/bin/python

# Standard Lib
import sys
import os
import random
import unittest
import yaml

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Include in path
#
# Recursively include in path:
# https://www.tutorialspoint.com/python/os_walk.htm
for root, dirs, files in os.walk("src/", topdown=False):
    for name in dirs:
        sys.path.append(root+'/'+name)

##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Developed
from data_manager import DataManager
from scheduler import Schedule
from schedule_util import KWH2KJ

##==============================================================================
#
class TestScheduleClass(unittest.TestCase):
    ##==========================================================================
    # Tests

    ##--------------------------------------------------------------------------
    #
    def test_schedule_generation_csv(self):
        # Create a schedule
        s = Schedule(None, "./src/config", "./data")
        return

    ##--------------------------------------------------------------------------
    #
    def test_schedule_discharge_calculation_csv(self):
        # Set the schedule to `csv'
        prev_state = self.__set_schedule('csv', "./src/config/")

        # Create a schedule
        s = Schedule(None, "./src/config", "./data")

        # Get the scheduled discharged values
        l = s.dm['l']

        # Pick compare charges
        b =  random.randint(0, s.dm['A']-1)

        # Calculate the discharge
        dis = self.__calcDischarge(s, b)

        # Compare discharge
        self.assertEqual(dis , l[b])

        # Reset state back to what it was
        self.__set_schedule(prev_state, "./src/config/")

        return

    ##--------------------------------------------------------------------------
    #
    def test_schedule_discharge_calculation_random(self):
        # Set the schedule to `csv'
        prev_state = self.__set_schedule('random', "./src/config/")

        # Create a schedule
        s = Schedule(None, "./src/config", "./data")

        # Get the scheduled discharged values
        l = s.dm['l']

        # Pick compare charges
        b = random.randint(0, s.dm['A']-1)

        # Calculate the discharge
        dis = self.__calcDischarge(s, b)

        # Compare discharge
        self.assertEqual(dis , l[b])

        # Reset state back to what it was
        self.__set_schedule(prev_state, "./src/config/")

        return


    ##==========================================================================
    # Helper functions

    ##--------------------------------------------------------------------------
    #
    def __calcDischarge(self, s: Schedule, b: int):
        """
        Helper function used to calculate the discharge of a bus over a
        given route.

        Input:
            - s : Schedule object
            - b : The identifier of the bus

        Ouput:
            - dis : The amount of energy lost during the route [KWh]
        """

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Variables
        visit_idx = [index for index, bus in enumerate(s.dm['Gamma']) if bus == b]
        depart    = s.dm['t'][visit_idx[0]]
        arrival   = s.dm['a'][visit_idx[1]]
        z         = s.dm['zeta'][b]                                             # Discharge rate for bus b

        ##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # Executable code
        return z*(arrival - depart)

    ##--------------------------------------------------------------------------
    #
    def __set_schedule(self, type: str, path: str):
        """
        Given the state type, update the YAML file to the correct schedule
        type.

        Input:
            - type: Type of schedule: 'random' or 'csv'
            - path: Base path to the YAML file

        Ouput:
            - prev: The previous state before updating to `type'
        """
        # Variables
        prev   = ""
        f_path = path+'general.yaml'

        # Executable code

        # Get the current state
        with open(f_path) as f:
            s = yaml.load(f, Loader=yaml.FullLoader)

        prev               = s['schedule_type']
        s['schedule_type'] = type

        # Update file with new state
        with open(f_path, 'w') as f:
            yaml.dump(s, f)

        return prev
