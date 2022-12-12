# Developed
from dict_util import *

##===============================================================================
#
class DataManager(object):
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    #
    def __new__(cls):
        """
        Override the instanciation of the objects to behave like a singleton

        References:
        https://www.geeksforgeeks.org/singleton-pattern-in-python-a-complete-guide/
        https://radek.io/2011/07/21/static-variables-and-methods-in-python/

        Input:
          NONE

        Output:
          NONE

        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataManager, cls).__new__(cls)

        return cls.instance

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   NONE
    #
    def __init__(self):
        # If DataManager has not been created yet, create it
        if not DataManager.m_schedule_data:
            ## Combine parameters and decision variables
            DataManager.m_schedule_data = \
                    merge_dicts(DataManager.m_params.copy(),
                                DataManager.m_decision_var.copy())

            ## Append the gurobi model to the dictionary
            DataManager.m_schedule_data = \
                    merge_dicts(DataManager.m_schedule_data, {'model' : None})
        return

    ##---------------------------------------------------------------------------
    # Input:
    #   key: Key for the dictionary
    #   val: Value to be inserted
    #
    # Output:
    #   key_exists: Returns of the key exists (value was saved)
    #
    def set(self, key, val):
        key_exists = False

        # Check if the schedule has the specified key, if so update schdule
        # parameter
        if DataManager.m_schedule_data.__contains__(key):
            key_exists = True

            DataManager.m_schedule_data[key] = val

            ## Check if input parameter contains the key,
            ## if so update its value
            if DataManager.m_params.__contains__(key):
                DataManager.m_params[key] = val

            ## Otherwise decision variable contains the key,
            ## if so update its value
            else:
                DataManager.m_decision_var[key] = val

        return key_exists

    ##---------------------------------------------------------------------------
    # Input:
    #   keys: List of keys for the dictionary
    #   vals: List of values to be inserted
    #
    # Output:
    #   key_exists: Returns list of key existence in dict (value was saved)
    #
    def setList(self, keys, vals):
        key_exists = len(keys)*[None]

        # Check if the schedule has the specified key, if so update schdule
        # parameter
        for ke,k,v in zip(key_exists, keys,vals):
            ke = DataManager.set(self, k, v)

        return key_exists

    ##---------------------------------------------------------------------------
    # Input:
    #   key: Key for the dictionary
    #
    # Output:
    #   value: The value associated with the specified key
    #
    def __getitem__(DataManager, key):
        if DataManager.m_schedule_data.__contains__(key):
            return DataManager.m_schedule_data[key]
        else:
            print("ERROR: Invalid key provided!")
            print(quit)
            quit()

    ##---------------------------------------------------------------------------
    # Input:
    #   key: Key for the dictionary
    #
    # Output:
    #   key_exists: Returns of the key exists (value was saved)
    #
    def __setitem__(self, key, value):
        return DataManager.set(self, key,value)

    ##===========================================================================
    # PRIVATE

    ##---------------------------------------------------------------------------
    # STATIC VARIABLES

    # Input Variables
    m_params = \
    {
        'A'      : None, #  Number of buses
        'Gamma'  : None, #  Array of visit ID's
        'N'      : None, #  Number of total visits
        'Q'      : None, #  Number of chargers
        'S'      : None, #  Length of a single charger
        'T'      : None, #  Time horizon                                        [hr]
        'K'      : None, #  Discrete number of steps in T
        'a'      : None, #  Arrival time of bus visit i                         [hr]
        'alpha'  : None, #  Initial charge percentage for bus a                 [%]
        'beta'   : None, #  Final charge percentage for bus a at T              [%]
        'dt'     : None, #  Discrete time step                                  [hr]
        'e'      : None, #  (epsilon) Cost of using charger q per unit time
        'gamma'  : None, #  Array of values indicating the next index for bus i
        'kappa'  : None, #  Battery capacity for bus i                          [MJ]
        'l'      : None, #  (lambda) Discharge of bus visit over route i
        'm'      : None, #  Cost of bus i being assigned to charger q
        'maxr'   : None, #  Maximum rest time between routes                    [hr]
        'minr'   : None, #  Minimum rest time between routes                    [hr]
        'nu'     : None, #  Minimum charge allowed on departure of visit i      [%]
        'r'      : None, #  Charge rate for charger q                           [KWh]
        's'      : None, #  Length of a bus
        't'      : None, #  (tau) Departure time for bus visit i                [hr]
        'tk'     : None, #  Array of discrete times                             [hr]
        'zeta'   : None, #  Discharge rate for bus a                            [KW]
        'slow'   : None, # Number of slow chargers
        'fast'   : None, # Number of fast chargers
    }

    # Decision Variables
    m_decision_var = \
    {
        'c'     : None, #  Detatch time for visit i                         [hr]
        'delta' : None, #  Determines if i is "fully left" of j
        'eta'   : None, #  Initial charge for bus visit i                   [MJ]
        'g'     : None, #  Linearization for bilinear term g := p[i]*w[i][q]
        'p'     : None, #  Time to charge for bus visit i                   [hr]
        'sigma' : None, #  Determines if i is "fully below" j
        'u'     : None, #  Initial charge time for visit i                  [hr]
        'v'     : None, #  Assigned queue for visit i
        'w'     : None, #  Matrix represetntation of bus charger assignments
    }

    # Schedule
    m_schedule_data = None
