import os
import sys

current_dir = '/Users/mcallister/projects/INP/trajectories/Ucluelet_files/'
file_list = []
for root, dirs, files in os.walk(current_dir, topdown=False):
    for name in files:
		if name.startswith('Untitled'):
			file_list.append(name)




i = 0
current_dir = '/Users/mcallister/projects/INP/trajectories/Ucluelet_2013-3d/Ucluelet_2013-3d-50magl/'
for root, dirs, files in os.walk(current_dir, topdown=False):
	for name in files:
		if name in file_list:
			print name
			i += 1
		else:
			print 'removed ', name
			os.remove(os.path.join(root, name))

        
print len(file_list)
print i
