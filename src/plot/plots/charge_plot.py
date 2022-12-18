# System Modules
import matplotlib.pyplot as plt
import numpy             as np

# Developed Modules
from plot import Plotter
from grid_shader import GridShader

##===============================================================================
#
class ChargePlot(Plotter):
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
        Plotter.__init__(self, "charge")
        return

    ##-----------------------------------------------------------------------
    # Input:
    #           NONE
    #
    # Output:
    #           Plot of bus schedule
    #
    def plot(self):
        # Local Variables
        A       = self.A
        N       = self.N

        # Configure Plot
        fig, ax = plt.subplots(1)
        x,y     = self.__groupChargeResults(N, A, self.Gamma, self.eta, self.u, self.c, self.v, self.r, self.g)

        # Set the axis limits
        ax.set_xlim(0, 24)

        ax.set_title("BEB Charge")
        plt.xlabel("Time")
        plt.ylabel("Charge [kwh]")

        for i in range(A): ax.plot(x[i], y[i])

        # gs = GridShader(ax, facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(15,8)
        plt.savefig(self.outdir+'charges.pdf', transparent=True, dpi=100)

        plt.show()
        return

    ##=======================================================================
    # PRIVATE

    ##-----------------------------------------------------------------------------
    # Input:
    #   N     : Number of bus visits
    #   A     : Number of buses
    #   Gamma : Array of bus ID's
    #   eta   : Array of bus charges
    #   u     : Initial charge time
    #   c     : Detach time
    #   v     : Active charger
    #   r     : Charger rate
    #
    # Output:
    #   x : Array of incrementing values from 1 to N
    #   y : Array of charges for each bus
    #
    def __groupChargeResults(self, N, A, Gamma, eta, u, c, v, r,g):
        charges = []
        idx     = []

        # For every bus
        for j in range(A):
            tempx       = []
            tempy       = []

            ## For every visit
            for i in range(N):
                ### If the visit is for the bus of interest
                if Gamma[i] == j:
                    #### Append the charge on arrival
                    tempx.append(u[i])
                    tempy.append(eta[i])

                    #### Append the charge on departure
                    tempx.append(c[i])
                    tempy.append(eta[i] + g[i][int(v[i])]*r[int(v[i])])

            ### Update the plot arrays
            idx.append(tempx)
            charges.append(tempy)

        return idx, charges
