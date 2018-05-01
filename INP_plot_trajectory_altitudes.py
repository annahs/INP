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
from matplotlib.colors import LinearSegmentedColormap
import INP_source_apportionment_module as INPmod
from matplotlib.path import Path
import pickle
n=0
endpoints = {}
traj_file_location = '/Users/mcallister/projects/INP/MOSSI/trajectories/'
traj_file_location = '/Users/mcallister/projects/INP/trajectories/Alert-20d/sample7_4w_ens/'

os.chdir(traj_file_location)
for file in os.listdir('.'):
	#if file.startswith('INP_MOSSI_20140714-1241_alt15'):
	if file.startswith('INP_Alert_7_sample4_1504071932_alt4303'):
		with open(file,'r') as f:
			print file
			data_start = False
			for line in f:
				newline = line.split()

				if data_start == True:
					traj_number = float(newline[0])
					hours_along = float(newline[8])
					lat 		= float(newline[9])
					lon 		= float(newline[10])
					height 		= float(newline[11]) # in m AMSL
					rain 		= float(newline[13])
					mixed_depth = float(newline[14]) # in m AGL
					terrain_ht	= float(newline[15]) # in m
					endpoint 	= [hours_along,height]
					
					#if traj_number in [1+n,10+n,19+n]:
					if 0 < (traj_number) <= 9:

						if traj_number in endpoints:
							endpoints[traj_number].append(endpoint)
						else:
							endpoints[traj_number] = [endpoint]

				if newline[1] == 'PRESSURE':
					data_start = True


fig = plt.figure(figsize=(12,10))
ax1 = fig.add_subplot(111)

colors = ['b','g','r']
i=0
for trajectory in endpoints:
	print trajectory

	hours = [row[0] for row in endpoints[trajectory]]		
	alt   = [row[1] for row in endpoints[trajectory]]		

	ax1.plot(hours,alt, marker= 'o', color = 'r')
	i+=1
ax1.set_xlabel('Time')
plt.show()
