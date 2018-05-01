import os
import sys

current_dir = '/Users/mcallister/projects/INP/FLEXPART-WRF/'

for root, dirs, files in os.walk(current_dir, topdown=False):
    for name in files:
		if name.endswith('0.nc'):
			print name
			os.remove(os.path.join(root, name))
    
        
