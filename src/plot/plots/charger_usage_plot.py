# System Modules
import matplotlib.pyplot as plt
import numpy             as np

# Developed Modules
from plot import Plotter
from grid_shader import GridShader

##===============================================================================
#
class ChargerUsagePlot(Plotter):
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
        Plotter.__init__(self, "charger_usage")
        return

    ##-----------------------------------------------------------------------
    # Input:
    #           NONE
    #
    # Output:
    #   Plot of power usage
    #
    def plot(self):
        # Local Variables
        A = self.A
        N = self.N
        p = self.p
        r = self.r
        v = self.v
        u = self.u
        c = self.c

        v100 = []
        v400 = []

        # Configure Plot
        fig, ax = plt.subplots(2)

        for i in range(N):
            if self.v[i] <= 4:
                v100.append(self.v[i])
            else:
                v400.append(self.v[i])

        # Create arrays to count usages
        ## Unique chargers used
        u100   = len(set(v100))
        u400   = len(set(v400))

        ## Create array to count uses
        use100 = np.zeros(len(np.linspace(0,self.T,self.K)), dtype=int)
        use400 = np.zeros(len(np.linspace(0,self.T,self.K)), dtype=int)

        idx = 0
        for i in np.linspace(0,self.T,self.K):
            for j in range(N):
                if u[j] <= i and c[j] >= i:
                    if v[j] <= u100:
                        use100[idx] += 1
                    else:
                        use400[idx] += 1
            idx += 1

        ax[0].set_title("Slow Chargers")
        ax[1].set_title("Fast Chargers")
        ax[0].set(xlabel="Time [hr]", ylabel="Times Used")
        ax[1].set(xlabel="Time [hr]", ylabel="Times Used")

        # Plot restults
        n = self.dt

        ran = range(len(use100)-1)
        ax[0].plot([x*n for x in ran], use100[0:len(use100)-1])

        ran = range(len(use400)-1)
        ax[1].plot([x*n for x in ran], use400[0:len(use400)-1])

        gs = GridShader(ax[0], facecolor="lightgrey", first=False, alpha=0.7)
        gs = GridShader(ax[1], facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(5,10)
        plt.savefig(self.outdir+'usage.pdf')

        plt.show()
        return

    ##=======================================================================
    # PRIVATE
