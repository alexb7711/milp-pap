# Developed
from dict_util import *

##===============================================================================
#
class DataManager:
    ##===========================================================================
    # PUBLIC

    ##---------------------------------------------------------------------------
    # Input:
    #   NONE
    #
    # Output:
    #   NONE
    #
    def __init__(self):
        if self.m_schedule_data == None:
            self.m_schedule_data = merge_dicts(self.m_params, self.m_decision_var)
            self.m_schedule_data = merge_dicts(self.m_schedule_data, {'model' :None})
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
        if self.m_schedule_data.__contains__(key):
            key_exists = True

            self.m_schedule_data[key] = val

            ## Check if input parameter contains the key,
            ## if so update its value
            if self.m_params.__contains__(key):
                self.m_params[key] = val

            ## Otherwise decision variable contains the key,
            ## if so update its value
            else:
                self.m_decision_var[key] = val

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
            ke = self.set(k,v)

        return key_exists

    ##---------------------------------------------------------------------------
    # Input:
    #   key: Key for the dictionary
    #
    # Output:
    #   value: The value associated with the specified key
    #
    def __getitem__(self, key):
        if self.m_schedule_data.__contains__(key):
            return self.m_schedule_data[key]
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
        return self.set(key,value)

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
        'Q'      : None, #  Number of charters
        'T'      : None, #  Time horizon                                        [hr]
        'K'      : None, #  Discrete number of steps in T
        'a'      : None, #  Arrival time of bus i                               [hr]
        'alpha'  : None, #  Initial charge percentage for bus i                 [%]
        'beta'   : None, #  Final charge percentage for bus i at T              [%]
        'dt'     : None, #  Discrete time step                                  [hr]
        'e'      : None, #  (epsilon) Cost of using charger q per unit time
        'gamma'  : None, #  Array of values indicating the next index for bus i
        'kappa'  : None, #  Battery capacity for bus i                          [MJ]
        'l'      : None, #  (lambda) Discharge of bus visit over route i
        'm'      : None, #  Cost of bus i being assigned to charger q
        'maxrst' : None, #  Maximum rest time between routes                    [hr]
        'minrst' : None, #  Minimum rest time between routes                    [hr]
        'maxrt'  : None, #  Maximum rout time                                   [hr]
        'minrt'  : None, #  Minimum rout time                                   [hr]
        'nu'     : None, #  Minimum charge allowed on departure of visit i      [%]
        'r'      : None, #  Charge rate for charger q                           [KWh]
        't'      : None, #  (tau) Departe time for bus i
        'tk'     : None, #  Array of discrete times                             [hr]

    }

    # Decision Variables
    m_decision_var = \
    {
        'c'     : None, #  Detatch time for visit i                         [hr]
        'delta' : None, #  Determines if i is "fully left" of j
        'eta'   : None, #  Initial charge for bus visit i                   [MJ]
        'g'     : None, #  Linearization for bilinear term g := p[i]*w[i][q]
        'p'     : None, #  Time to charge for bus visit i                   [hr]
        'psi'   : None, #  Linearization term for power objective function
        'sigma' : None, #  Determines if i is "fully below" j
        'u'     : None, #  Initial charge time for visit i                  [hr]
        'v'     : None, #  Assigned queue for visit i
        'w'     : None, #  Matrix represetntation of bus charger assignments
        'xi'    : None, #  Binary term to determine bus i is charging in tk
    }

    # Schedule
    m_schedule_data = None
