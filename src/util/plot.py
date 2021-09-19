# System Modules
import matplotlib.pyplot as plt
import numpy             as np

from matplotlib.collections import PatchCollection
from matplotlib.patches     import Rectangle

# Developed Modules

##===============================================================================
#
class Plotter:
	##=======================================================================
	# PUBLIC

	##-----------------------------------------------------------------------
	# Input:
	#	Example: test
	#
	# Output:
	#	Example: test
	#
    def __init__(self, data):
        # Constants
        self.A     = data['A']
        self.N     = data['N']
        self.Q     = data['Q']

        # Input Vars
        self.a     = data['a']
        self.r     = data['r']
        self.t     = data['t']
        self.Gamma = data['Gamma']
        self.gamma = data['gamma']

        # Decision Vars
        self.c     = data['c']
        self.delta = data['delta']
        self.eta   = data['eta']
        self.p     = data['p']
        self.sigma = data['sigma']
        self.u     = data['u']
        self.v     = data['v']
        self.w     = data['w']
        self.g     = data['g']

        return

    ##-------------------------------------------------------------------------------
    # Input:
    #
    # Output:
    # Plot of bus schedule
    #
    def plotSchedule(self):
        fig, ax        = plt.subplots(1)
        time, position = self.__plotResults(self.N, ax, self.a, self.u, self.v, self.c)
        _              = self.__makeErrorBoxes(ax, self.u, self.v, time, position)

        plt.show()
        return

    ##-------------------------------------------------------------------------------
    # Input:
    #
    # Output:
    # Plot of bus schedule
    #
    def plotCharges(self):
        N       = self.N
        A       = self.A
        fig, ax = plt.subplots(1)
        x,y     = self.__groupChargeResults(N, A, self.Gamma, self.eta)

        for i in range(A):
            ax.plot(x, y[i])

        plt.show()

        return

    ##-------------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   Q : Number of chargers
    #   r : Charger rates
    #   v : Assigned charger for each visit
    #
    # Output:
    #   Plot of power usage
    #
    def plotChargerUsage(self):
        # Local Variables
        A = self.A
        N = self.N
        Q = self.Q
        r = self.r
        v = self.v

        fig, ax = plt.subplots(1)
        x,y     = self.__calculateUsage(N, Q, r, v)

        ax.plot(x, y)
        plt.show()

        return

	##=======================================================================
	# PRIVATE

    ##-------------------------------------------------------------------------------
    # Input:
    #   a: Arrival time
    #   u: Starting charge time
    #   v: Staring queue position
    #   c: Departure Time
    #
    # Output:
    #
    def __plotResults(self, N, ax, a, u, v, c):
        # Format error matrix
        pos_upper = []
        pos_lower = []
        tim_upper = []
        tim_lower = []

        for i in range(N):
            pos_lower.append(0)
            pos_upper.append(0.8)

            tim_lower.append(u[i] - a[i])
            tim_upper.append(c[i] - u[i])

        tim = np.vstack((tim_lower, tim_upper))
        pos = np.vstack((pos_lower, pos_upper))

        return tim, pos

    ##-------------------------------------------------------------------------------
    #
    def __makeErrorBoxes(self, ax, xdata, ydata, xerror, yerror, facecolor='r',
                         edgecolor='None', alpha=0.5):

        # Loop over data points; create box from errors at each point
        errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum())
                      for x, y, xe, ye in zip(xdata, ydata, xerror.T, yerror.T)]

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,
                             edgecolor=edgecolor)

        # Add collection to axes
        ax.add_collection(pc)

        print("Error Data")
        print(xerror)
        print(yerror)

        # Plot errorbars
        artists = ax.errorbar(xdata, ydata, xerr=xerror, yerr=yerror,
                              fmt='None', ecolor='k')

        return artists

    ##-------------------------------------------------------------------------------
    # Input:
    #   N     : Number of bus visits
    #   A     : Number of buses
    #   Gamma : Array of bus ID's
    #   eta   : Array of bus charges
    #
    # Output:
    #   x : Array of incrementing values from 1 to N
    #   y : Array of charges for each bus
    #
    def __groupChargeResults(self, N, A, Gamma, eta):
        charges = []

        for i in range(A):
            last_charge = 0
            temp = np.zeros(N)

            for j in range(self.N):
                if Gamma[j] == i:
                        temp[j] = last_charge = eta[j]
                else:
                    temp[j] = last_charge

            charges.append(temp)

        return range(0,N,1), charges

    ##-------------------------------------------------------------------------------
    # Input:
    #   N : Number of bus visits
    #   Q : Number of chargers
    #   r : Charger rates
    #   v : Assigned charger for each visit
    #
    # Output:
    #   x : Array of incrementing values from 1 to N
    #   y : Array of total charger usage at each bus visit
    #
    def __calculateUsage(self,N, Q, r, v):
        usage = np.zeros(N)

        for i in range(N):
            charger = int(v[i] - 1)
            if i == 0:
                usage[i] = r[charger]

            usage[i] = usage[i-1] + r[charger]

        return range(0,N,1), usage
