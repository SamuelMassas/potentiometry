from matplotlib.backend_bases import MouseButton
import matplotlib
from matplotlib.figure import Figure
import numpy as np
import json


class Series(matplotlib.lines.Line2D):
    def __init__(self):
        super().__init__(xdata=[], ydata=[])  # Initializing line


a = Series()

print()