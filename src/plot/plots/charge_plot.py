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
        x,y     = self.__groupChargeResults(N, A, self.Gamma, self.eta, self.u)

        plt.xlabel("Time")
        plt.ylabel("Charge [kwh]")

        for i in range(A):
            ax.plot(x[i], y[i])

        gs = GridShader(ax, facecolor="lightgrey", first=False, alpha=0.7)

        plt.savefig(self.outdir+'charges.pdf')

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
    #
    # Output:
    #   x : Array of incrementing values from 1 to N
    #   y : Array of charges for each bus
    #
    def __groupChargeResults(self, N, A, Gamma, eta, u):
        charges = []
        idx     = []

        for i in range(A):
            last_charge = 0
            tempx       = []
            tempy       = []

            for j in range(N):
                if Gamma[j] == i:
                    tempx.append(u[j])
                    tempy.append(eta[j])
                    last_charge = eta[j]
                elif last_charge == 0:
                    continue

            idx.append(tempx)
            charges.append(tempy)

        return idx, charges
