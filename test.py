import os
import sys
from pprint import pprint
lines = []
file = '/Users/mcallister/projects/INP/INP/Alert_10d_parameters.txt'
i = 1
with open(file, 'r') as f:
	for line in f:
		newline = line.split()
		if newline[0].startswith('hours'):
			a= newline[1]
		if newline[0] == 'desert':
			b= newline[3]
		if newline[0] == 'sea':
			c= newline[4]
		if newline[0] == 'open':
			d= newline[4]
		if i%7 == 0:	
			lines.append([a,b,c,d])
		i+=1
	pprint(lines)



