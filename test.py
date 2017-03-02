import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import os
import sys
from pprint import pprint
from datetime import datetime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import matplotlib.colors
from dateutil import parser
import math
import shapefile
import argparse
import INP_source_apportionment_module as INPmod

lon_bins = np.linspace(0, 5, 5+1)
lat_bins = np.linspace(0, 5, 5+1)

xs = [1,1,3,4,5]
ys = [0,0,2,3,4]


a,b,c= np.histogram2d(ys, xs, [lat_bins, lon_bins])
g,h,i= np.histogram2d(ys, xs, [lat_bins, lon_bins])
print a
print g
print np.dstack((a,g))