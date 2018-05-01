#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys   
reload(sys)  
sys.setdefaultencoding('utf8')   
import numpy as np                         
import matplotlib.pyplot as plt            
from matplotlib import cm                  
import matplotlib.colors as mcolors   
from mpl_toolkits.basemap import Basemap     
import h5py                                                             
import os 
import glob
from pprint import pprint
import calendar
import dateutil
import FLEXPART_PES_NETCARE_module as PES
import argparse

def get_tracer(pfiley, variable, dimlist, Ntimes):
  print ("***  getting ", variable, " from file "+pfiley+" with dimensions ", dimlist, " ***")
  ff = h5py.File(pfiley, mode='r')
  dset = np.zeros((dimlist[3], dimlist[4], dimlist[5]))

  for i in range(1,Ntimes):#start with the second time step, the first one contains zero concentration

    if i%1000 == 0: #check progress
      print(i)

    ds = ff[variable][i,0,0,:,:,:] #The variable CONC has shape (time, ageclass, releases, height(Z  - top/bottom), latitude (X - north/south), longitude (Y - west/east) )
    dset = ds + dset

  data = np.array(dset)
  del(dset)
  ff.close()
  return data



n_header = 'header_d01.nc'  
dfolder  = '/Users/mcallister/projects/INP/FLEXPART-WRF/ship-14July-backward/output_00781/'
p_header = os.path.join(dfolder,n_header)

start_str,date_str,p_data = PES.getDataPathFromFilename(dfolder)

#sometimes a folder is missong the .nc file, in this case skip it
if p_data == None:
	print 'no pdata'
	sys.exit()

##look at the main Flexpart output .nc file
f_tracer = h5py.File(p_data, mode = 'r')

##get grid and dimension information
xlat = PES.get_var(p_header, 'XLAT')
Nlat = len(xlat)

xlon = PES.get_var(p_header, 'XLONG')
Nlon = len(xlon)

ztop = PES.get_var(p_header, 'ZTOP') #Ztop = top of vertical levels in meters = [10, 100, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 4000, 5000, 20,000]
Ntop = len(ztop)

times = PES.get_var(p_data, 'Times')
Ntimes = times.shape[0] #same as len(times)

ageclass = PES.get_var(p_data, 'ageclass')
Nage = len(ageclass)

releases = PES.get_var(p_data, 'releases')
Nrel = len(releases)

dimlist = [Ntimes, Nage, Nrel, Ntop, Nlat, Nlon]
print("Dimensions of CONC variable = " + str(dimlist))


##get PES(residence time) 3D and 2D arrays
for i in range(1,Ntimes):#start with the second time step, the first one contains zero concentration

	dset = f_tracer['CONC'][i,0,0,:,:,:] #The variable CONC has shape (time, ageclass, releases, height(Z  - top/bottom), latitude (X - north/south), longitude (Y - west/east) )
	Conc = np.array(dset)
	temp = Conc[0:4,:,:]
	Conc_pCol300 = np.sum(temp, axis=0)

	#create a basemap instance
	fig = plt.figure(figsize=(10,10))
	m = Basemap(width=4700000,height=4700000, resolution='l',projection='stere',lat_0=70,lon_0=-83.)

	#re-project the FLEXPART grid
	x,y=m(xlon,xlat)

	#draw the map details
	m.drawcoastlines(linewidth=0.5)
	m.drawmapboundary(fill_color = 'w', zorder = 0)
	m.fillcontinents(color = 'w', lake_color = 'w', zorder=0)
	parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
	m.drawparallels(parallels,labels=[False,True,True,False])
	meridians = np.arange(10.,351.,20.)
	m.drawmeridians(meridians,labels=[True,False,False,True])

	#make the PES contour plot 
	levels = ([0.001,0.01,0.05,0.1,0.5,1,5.0,10.,50.,100.,500.,1000.,5000])
	color_list = ['#FFFFFF','#BBE3F9','#76BDEB','#408ACC','#3E967D','#5BBA33','#CFDC44','#FBAA2D','#F4561E','#D32E1E','#B21819','#8B1214']
	cols=PES.makeColormap(color_list)
	norm = mcolors.BoundaryNorm(levels,ncolors=cols.N, clip=False)
	cs = m.contourf(x,y,Conc_pCol300, levels=levels, cmap=cols,  norm=norm) # this code is currently only plotting the total column PES

	#add a scale bar
	#cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.015])
	cbar=plt.colorbar(cs, format="%.2f", orientation="horizontal",fraction=.06, pad=0.08)
	cbar.set_label('FLEXPART-WRF residence time (s)')

	xs,ys = m(-61.08522,67.24028167)
	m.scatter(xs,ys,marker = 'o',zorder = 100, color = 'k', s=50)

	os.chdir('/Users/mcallister/projects/INP/FLEXPART-WRF/hourly plots/')
	plt.savefig('FLEXPART-WRF_hourly_0-300m_'+ date_str + '_' + str(i) + '_AmundsenINP.png', bbox_inches='tight', dpi=300)
	#plt.show()
	plt.close()

