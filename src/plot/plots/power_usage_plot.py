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
	#			name: Name of the plot
	#
	# Output:
	#	Example: test
	#
	def __init__(self):
		self._name = "power_usage_plot"
		return
	
	##-----------------------------------------------------------------------
	# Input:
	#			NONE
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
		fig, ax = plt.subplots(1)

		## Create array to count uses
		usage = np.zeros(len(np.linspace(0,self.T,1000)), dtype=int)
		dt = self.T/1000

		idx = 0
		for i in np.linspace(0,self.T,1000):
			for j in range(self.A+self.N):
				if u[j] <= i and c[j] >= i:
					usage[j] += r[int(v[j])]*dt
			idx += 1

		ax.set_title("Power Usage")
		ax.set(xlabel="Time [hr]", ylabel="Usage [KWh]")

		# Plot restults
		n = 1.0/100

		ran = range(len(usage)-1)
		ax.plot([x*n for x in ran], usage[0:len(usage)-1])

		gs = GridShader(ax, facecolor="lightgrey", first=False, alpha=0.7)

		fig.set_size_inches(5,10)
		plt.savefig('power_usage.pdf')

		plt.show()
		return

	##=======================================================================
	# PRIVATE

	##-----------------------------------------------------------------------
	# Input:
	#			name: Name of the plot
	#
	# Output:
	#			slow_count: Number of slow chargers
	#			fast_count: Number of fast chargers
	#
	def __countChargers(self):
		# Local Variables
		slow_count  = []
		fast_count  = []
		slow_charge = 100;
		fast_charge = 450;

		for i in range(self.A+self.N):
			if self.r(self.v[i]) <= slow_charge:
				slow_count.append(self.v[i])
			else:
				fast_count.append(self.v[i])
		return v100, v400
