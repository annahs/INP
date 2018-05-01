#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  
import os
import numpy as np    
from pprint import pprint
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D           
import FLEXPART_PES_NETCARE_module as PES
from scipy import stats


#Sample ID	Sample date	INP/L at -15ºC	INP/L at -25ºC	Minearl dust 1	sea salt 2

data=[
#[1,		'03/11/2016',	np.nan,			np.nan,			-0.86759,	-0.58451],
[3,		'03/13/2016',	0.006667062,	0.094872405,	-1.20549,	-0.61254],
[4,		'03/14/2016',	0.010930761,	0.074331362,	-0.15087,	0.12087	],
[5,		'03/15/2016',	0.012197541,	0.274653072,	0.06549	,	0.01286	],
[6,		'03/16/2016',	np.nan,			0.052102251,	-1.34921,	-0.58616],
[7,		'03/17/2016',	0.005882624,	0.036037524,	-1.32662,	-0.47098],
[8,		'03/18/2016',	0.028557448,	0.091594636,	-1.15033,	0.73562	],
[9,		'03/19/2016',	np.nan,			0.155272997,	-0.40589,	0.67151 ],
[10,	'03/20/2016',	0.006097561,	0.069098648,	-0.29535,	2.61224	],
[11,	'03/21/2016',	0.020095753,	0.061585439,	1.41125	,	1.94342	],
[12,	'03/22/2016',	0.01117377,		0.246090569,	1.3024	,	0.10711	],
[13,	'03/23/2016',	0.005952381,	0.160890087,	0.07962	,	-0.29679],
[14,	'03/24/2016',	np.nan,			0.337605602,	0.91105	,	-0.5055 ],
[16,	'03/26/2016',	np.nan,			0.192599774,	-0.03744,	-0.57092],
[17,	'03/27/2016',	np.nan,			0.518718759,	1.24458	,	-0.87412],
[18,	'03/28/2016',	np.nan,			0.541414483,	1.58098	,	-1.18008],
]



sample = [row[0] for row in data]
dates = [PES.valid_date(row[1]).day for row in data]
INP15 = [row[2] for row in data]
INP25 = [row[3]*400 for row in data]
MD    = [row[4] for row in data]
SS    = [row[5] for row in data]

varx = MD
vary = SS
varz = INP25


#define the figure
fig = plt.figure()
axes = fig.add_subplot(111, projection='3d')
#axes.scatter(varx,vary,varz,c=dates,cmap='Blues')
axes.scatter(varx,vary,varz)
axes.set_ylim(-2,3)
axes.set_xlim(3,-2)
axes.set_xlabel('MD')
axes.set_ylabel('SS')
axes.set_zlabel('INP')

#slope1, intercept1, r_value1, p_value1, std_err1 = stats.linregress(varx,vary)
#y_fits = []
#x_fits = np.arange(min(varx), max(varx)+0.1,0.1)
#for val in x_fits:
#	y_fit = val*slope1 + intercept1
#	y_fits.append(y_fit)
#axes.plot(x_fits,y_fits)
#axes.text(0.2, 0.67,'$r^2$ = '+str(round(r_value1*r_value1,4)),transform=axes.transAxes)
#axes.text(0.2, 0.62,'p-value = '+str(round(p_value1,4)),transform=axes.transAxes)

plt.show()

#define the figure
fig = plt.figure()
axes = fig.add_subplot(111)
axes.scatter(varx,vary,c=varz,cmap='jet',s=varz)
axes.set_ylim(-2,3)
axes.set_xlim(-2,3)
axes.set_xlabel('Mineral dust factor')
axes.set_ylabel('Sea salt factor')

plt.savefig('/Users/mcallister/projects/INP/Alert_INP2016/bin/Alert2016_SSvMD_colored_by_INP25.png',bbox_inches='tight')

plt.show()






