##===============================================================================
# PUBLIC

##-------------------------------------------------------------------------------
#
def genInputParams(self):
    """
    This helper function gets the input parameters for both random and CSV
    route generation.

    Input:
      - self: schedule object

    Output:
      - NONE
    """
    # Variables
    type    = self.schedule_type                                                # random or csv
    r       = np.concatenate((slow_chargers, fast_chargers))                    # Charge rates
    epsilon = [1]*len(r)                                                        # Usage cost
    m       = [1000*x for x in range(int(init['buses']['num_bus']))]            # Assignment cost

    # If the routes are randomly generated
    if type == 'random':
        self.dm['A']     = init['buses']['num_bus']                             # Number of buses
        self.dm['N']     = init['buses']['num_visit']                           # Number of bus visits
        self.dm['S']     = self.dm['Q']                                         # Singular charger size
        self.dm['K']     = init['time']['K']                                    # Total number of discrete steps
        self.dm['dt']    = self.dm['T']/self.dm['K']                            # Calculate discrete time step
        self.dm['maxr']  = init['buses']['max_rest']                            # Maximum/Minimum rest time between bus routes
        self.dm['minr']  = init['buses']['min_rest']
        self.dm['s']     = np.repeat(init['buses']['bus_length'], self.dm['N']) # Length of a bus
        self.dm['tk']    = \                                                    # Discrete time steps
                np.array([i*self.dm['dt'] for i in range(0,self.dm['K'])]);

    self.dm['Q']     = \                                                        # Number of chargers
    self.dm['T']     = init['time']['time_horizon']                             # Time horizon
        init['chargers']['slow']['num'] + init['chargers']['fast']['num']
    self.dm['alpha'] = initArray(self.dm['A'], dtype=float)                     # Initial charge percentages
    self.dm['beta']  = initArray(self.dm['N'], dtype=float)                     # Final charge percentages
    self.dm['e']     = epsilon                                                  # Cost of use for charger q
    self.dm['kappa'] = np.repeat(init['buses']['bat_capacity'], self.dm['A'])   # Battery capacity of each bus
    self.dm['m']     = m                                                        # Cost of assignment for charger q
    self.dm['nu']    = init['buses']['min_charge']                              # Minimum charge allowed on next visit
    self.dm['r']     = r                                                        # Charge rate for bus q
    self.dm['zeta']  = \                                                        # Discharge rate
        np.repeat([init['buses']['dis_rate']], init['buses']['num_bus'])



    return
