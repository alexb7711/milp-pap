# System Modules
import matplotlib.pyplot as plt
import numpy             as np

# Developed Modules
from plot import Plotter
from grid_shader import GridShader

##===============================================================================
#
class PowerUsagePlot(Plotter):
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
        Plotter.__init__(self, "power_usage_plot")
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

        # Configure Plot
        fig, ax = plt.subplots(1)

        ## Create array to count uses
        usage = np.zeros(len(np.linspace(0,self.T, self.K)), dtype=int)

        idx = 0
        for i in np.linspace(0,self.T,self.K):
            for j in range(N):
                if u[j] <= i and c[j] >= i:
                    usage[idx] += r[int(v[j])]
            idx += 1

        ax.set_title("Power Usage")
        ax.set(xlabel="Time [hr]", ylabel="Usage [KW]")

        # Plot restults
        n = self.dt

        ran = range(len(usage)-1)
        ax.plot([x*n for x in ran], usage[0:len(usage)-1])

        gs = GridShader(ax, facecolor="lightgrey", first=False, alpha=0.7)

        fig.set_size_inches(5,10)
        plt.savefig(self.outdir+'power_usage.pdf')

        plt.show()
        return

    ##=======================================================================
    # PRIVATE
