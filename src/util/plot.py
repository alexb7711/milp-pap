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
        # Configure Plot
        fig, ax = plt.subplots(2)
        a100    = []
        c100    = []
        u100    = []
        v100    = []

        a400    = []
        c400    = []
        u400    = []
        v400    = []

        for i in range(self.A+self.N):
            if self.v[i] <= 4:
                a100.append(self.a[i])
                c100.append(self.c[i])
                u100.append(self.u[i])
                v100.append(self.v[i])
            else:
                a400.append(self.a[i])
                c400.append(self.c[i])
                u400.append(self.u[i])
                v400.append(self.v[i])

        time100, position100 = self.__plotResults(len(v100), ax[0], a100, u100, v100, c100)
        _                    = self.__makeErrorBoxes(ax[0], u100, v100, time100, position100)

        time400, position400 = self.__plotResults(len(v400), ax[1], a400, u400, v400, c400)
        _                    = self.__makeErrorBoxes(ax[1], u400, v400, time400, position400)

        ax[0].set_title("Slow Chargers")
        ax[1].set_title("Fast Chargers")

        ax[0].set(xlabel="Time [hr]", ylabel="Queue")
        ax[1].set(xlabel="Time [hr]", ylabel="Queue")

        gs = GridShader(ax[0], facecolor="lightgrey", first=False, alpha=0.7)
        gs = GridShader(ax[1], facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(25,10)
        plt.savefig('schedule.pdf', dpi=100)

        plt.show()
        return

    ##-------------------------------------------------------------------------------
    # Input:
    #
    # Output:
    # Plot of bus schedule
    #
    def plotCharges(self):
        # Local Variables
        A       = self.A
        N       = self.N

        # Configure Plot
        fig, ax = plt.subplots(1)
        x,y     = self.__groupChargeResults(N, A, self.Gamma, self.eta)

        plt.xlabel("Time")
        plt.ylabel("Charge [kwh]")

        for i in range(A):
            ax.plot(x[i], y[i])

        gs = GridShader(ax, facecolor="lightgrey", first=False, alpha=0.7)

        plt.savefig('charges.pdf')


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
        p = self.p
        r = self.r
        v = self.v

        v100    = []
        v400    = []

        # Configure Plot
        fig, ax = plt.subplots(2)

        for i in range(self.A+self.N):
            if self.v[i] <= 4:
                v100.append(self.v[i])
            else:
                v400.append(self.v[i])

        # Create arrays to count usages
        ## Unique chargers used
        u100   = len(set(v100))
        u400   = len(set(v400))

        ## Create matricies to count uses
        use100 = np.zeros((u100,self.A+self.N), dtype=int)
        use400 = np.zeros((u400,self.A+self.N), dtype=int)

        for i in range(self.A+self.Q):
            idx = int(v[i]-1)
            if v[i] <= u100:
                use100[idx,i:] += 1
            else:
                use400[idx-u100,i:] += 1

        ax[0].set_title("Slow Chargers")
        ax[1].set_title("Fast Chargers")
        ax[0].set(xlabel="Time [hr]", ylabel="Times Used")
        ax[1].set(xlabel="Time [hr]", ylabel="Times Used")

        # Plot restults
        n = 1.0/10

        for i in range(u100):
            ran = range(len(use100[i]))
            ax[0].plot([x*n for x in ran], use100[i])

        for i in range(u400):
            ran = range(len(use400[i]))
            ax[1].plot([x*n for x in ran], use400[i])

        gs = GridShader(ax[0], facecolor="lightgrey", first=False, alpha=0.7)
        gs = GridShader(ax[1], facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(25,25)
        plt.savefig('usage.pdf', dpi=100)

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

        facecolor = ['#%06X' % np.random.randint(0, 0xFFFFFF) for i in range(self.N+self.A)]

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,
                             edgecolor=edgecolor)

        # Add collection to axes
        ax.add_collection(pc)

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
        idx     = []

        for i in range(A):
            last_charge = 0
            tempx       = []
            tempy       = []

            for j in range(N+A):
                if Gamma[j] == i:
                    tempx.append(j)
                    tempy.append(eta[j])
                    last_charge = eta[j]
                elif last_charge == 0:
                    continue
                else:
                    tempx.append(j)
                    tempy.append(last_charge)

            idx.append(tempx)
            charges.append(tempy)

        idx = [[x*(1.0/10) for x in y] for y in idx]

        return idx, charges

##===============================================================================
# https://stackoverflow.com/questions/54652114/matplotlib-how-can-i-add-an-alternating-background-color-when-i-have-dates-on-t
class GridShader():
	##=======================================================================
	# PUBLIC

    ##-------------------------------------------------------------------------------
    # Input:
    def __init__(self, ax, first      = True, **kwargs):
        self.spans                    = []
        self.sf                       = first
        self.ax                       = ax
        self.kw                       = kwargs

        #  self.ax.autoscale(False, axis = "x")

        self.cid = self.ax.callbacks.connect('xlim_changed', self.__shade)

        self.__shade()
        return

    ##=======================================================================
	# PRIVATE

    ##-------------------------------------------------------------------------------
    # Input:
    def __clear(self):
        for span in self.spans:
            try:
                span.remove()
            except:
                pass

    ##-------------------------------------------------------------------------------
    # Input:
    def __shade(self, evt=None):
        self.__clear()

        xticks = self.ax.get_xticks()
        xlim   = self.ax.get_xlim()
        xticks = xticks[(xticks > xlim[0]) & (xticks < xlim[-1])]
        locs   = np.concatenate(([[xlim[0]], xticks, [xlim[-1]]]))

        start = locs[1-int(self.sf)::2]
        end = locs[2-int(self.sf)::2]

        for s, e in zip(start, end):
            self.spans.append(self.ax.axvspan(s, e, zorder=0, **self.kw))
        return
