# System Modules
import matplotlib.pyplot as plt
import numpy             as np

# Developed Modules

##===============================================================================
# https://stackoverflow.com/questions/54652114/matplotlib-how-can-i-add-an-alternating-background-color-when-i-have-dates-on-t
class GridShader():
##===============================================================================
# PUBLIC

	##-----------------------------------------------------------------------------
	# Input:
	def __init__(self, ax, first = True, **kwargs):
		self.spans = []
		self.sf    = first
		self.ax    = ax
		self.kw    = kwargs

		self.cid = self.ax.callbacks.connect('xlim_changed', self.__shade)

		self.__shade()
		return

	##=============================================================================
	# PRIVATE

	##-----------------------------------------------------------------------------
	# Input:
	def __clear(self):
		for span in self.spans:
			try:
				span.remove()
			except:
				pass
		return

	##-----------------------------------------------------------------------------
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
