# System Modules
import matplotlib.pyplot as plt
import numpy             as np

from matplotlib.collections import PatchCollection
from matplotlib.patches     import Rectangle

# Developed Modules
from plot        import Plotter
from grid_shader import GridShader

##===============================================================================
#
class SchedulePlot(Plotter):
    ##=======================================================================
    # PUBLIC

    ##-----------------------------------------------------------------------
    # Input:
    #           name: Name of the plot
    #
    # Output:
    #   Example: test
    #
    def __init__(self):
        Plotter.__init__(self, "schedule")
        return

    ##-----------------------------------------------------------------------
    # Input:
    #           name: Name of the plot
    #
    # Output:
    #   Example: test
    #
    def plot(self):
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

        for i in range(self.N):
            if self.v[i] <= 5:                                                  # Number of slow chargers
                a100.append(self.a[i])
                c100.append(self.c[i])
                u100.append(self.u[i])
                v100.append(self.v[i])
            else:                                                               # Fast chargers
                a400.append(self.a[i])
                c400.append(self.c[i])
                u400.append(self.u[i])
                v400.append(self.v[i])

        # Create a unique color for each bus
        color     = ['#%06X' % np.random.randint(0, 0xFFFFFF) for i in range(self.A)]
        facecolor = [color[self.Gamma[x]] for x in range(self.N)]

        time100, position100 = self.__plotResults(len(v100), ax[0], a100, u100, v100, c100)
        _                    = self.__makeErrorBoxes(ax[0], u100, v100, time100, position100, facecolor)

        time400, position400 = self.__plotResults(len(v400), ax[1], a400, u400, v400, c400)
        _                    = self.__makeErrorBoxes(ax[1], u400, v400, time400, position400, facecolor)

        ax[0].set_title("Slow Chargers")
        ax[1].set_title("Fast Chargers")

        ax[0].set(xlabel="Time [hr]", ylabel="Queue")
        ax[1].set(xlabel="Time [hr]", ylabel="Queue")

        gs = GridShader(ax[0], facecolor="lightgrey", first=False, alpha=0.7)
        gs = GridShader(ax[1], facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(25,10)

        plt.savefig(self.outdir+'schedule.pdf', dpi=100)

        plt.show()

        fig, ax = plt.subplots(1)
        time100, position100 = self.__plotResults(len(v100), ax, a100, u100, v100, c100)
        _                    = self.__makeErrorBoxes(ax, u100, v100, time100, position100, facecolor)

        fig.set_size_inches(25,10)

        plt.show()
        return

    ##=======================================================================
    # PRIVATE

    ##-----------------------------------------------------------------------------
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

            tim_lower.append(self.__round_up(u[i] - a[i]))
            tim_upper.append(self.__round_up(c[i] - u[i]))

        tim = np.vstack((tim_lower, tim_upper))
        pos = np.vstack((pos_lower, pos_upper))

        return tim, pos

    ##-----------------------------------------------------------------------------
    #
    def __makeErrorBoxes(self, ax, xdata, ydata, xerror, yerror, facecolor='r',
                                             edgecolor='None', alpha=0.5):

        # Loop over data points; create box from errors at each point
        errorboxes = [Rectangle((x - xe[0], y - ye[0]), xe.sum(), ye.sum())
                                    for x, y, xe, ye in zip(xdata, ydata, xerror.T, yerror.T)]

        #  facecolor = ['#%06X' % np.random.randint(0, 0xFFFFFF) for i in range(self.N+self.A)]

        # Create patch collection with specified colour/alpha
        pc = PatchCollection(errorboxes, facecolor=facecolor, alpha=alpha,
                                                 edgecolor=edgecolor)

        # Add collection to axes
        ax.add_collection(pc)

        # Plot errorbars
        artists = ax.errorbar(xdata, ydata, xerr=xerror, yerr=yerror, fmt='None', ecolor='k')

        return artists

    ##-----------------------------------------------------------------------------
    #
    def __round_up(self, val):
        """Sometimes the difference of numbers is so small it shows up as a super
        small negative number, this method will round that up to 0.

        * INPUT
          - `val`: Number to be checked

        * OUTPUT
          - `val`: Update value
        """

        # Local Variables
        tol = 1e-10

        if val <= tol:
            return 0.0

        return val
