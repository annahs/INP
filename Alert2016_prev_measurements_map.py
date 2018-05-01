#!/usr/bin/env python
# -- coding: UTF-8 --
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import os
import numpy as np                         
import matplotlib.pyplot as plt            
from mpl_toolkits.basemap import Basemap
import dateutil
from pprint import pprint
from datetime import datetime
from matplotlib.path import Path
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.colors as mcolors  
import pandas as pd
from matplotlib import rc

# activate latex text rendering
rc('text', usetex=False)
#define the figure
fig, axes = plt.subplots(1,1,figsize=(14, 14))
                 
#create a basemap instance
m = Basemap(width=8000000,height=8000000, resolution='l',projection='stere',lat_0=90,lon_0=-83.,rsphere=6378137.0)
m.fillcontinents(color = 'lightgrey', lake_color = 'w')
m.drawcoastlines(linewidth=0.5)
m.drawcountries()
parallels = np.arange(0.,81,10.) # labels = [left,right,top,bottom]
m.drawparallels(parallels,labels=[False,True,True,False])
meridians = np.arange(10.,351.,20.)
m.drawmeridians(meridians,labels=[True,False,False,True])

#add measurements
prev_measurements_file = '/Users/mcallister/projects/INP/Alert_INP2016/docs/Previous Arctic measurements locations.csv'
df = pd.read_csv(prev_measurements_file)
#pprint(df)


m_colors = [
'm', 
'peru',
'k',
'g',
'r',
'orange',
'b', 
'brown',
'yellow',
'navy',
'darkgreen',
'cyan',
'purple'
]


i=0
print '*** Ground stations ***'
for measurement in  df.loc[df['platform'] == 'Ground'].values.tolist():
	print measurement[0]
	x,y = m(measurement[2],measurement[3])
	m.scatter(x,y,marker = '*',s=150,zorder = 150, color = m_colors[i],label=measurement[0])
	i+=1

print '*** Aircraft stations ***'
aircraft = df.loc[df['platform'] == 'Aircraft']
pubs =  aircraft.groupby(['Publication'])
for name, group in pubs:
	print name
	Longitudes = group['Longitude'].tolist()
	Latitudes  = group['Latitude'].tolist()
	x,y = m(Longitudes,Latitudes)
	m.plot(x,y,marker = 'None',linewidth=1.75,zorder = 100,alpha=1,linestyle='-' ,color = m_colors[i])
	xi,yi = m(Longitudes[0],Latitudes[0])
	m.scatter(xi,yi,marker = '>',s=100,zorder = 100,alpha=1, color = m_colors[i],label=name)
	i+=1

print '*** Icebreaker stations ***'
aircraft = df.loc[df['platform'] == 'Icebreaker']
pubs =  aircraft.groupby(['Publication'])
for name, group in pubs:
	print name
	Longitudes = group['Longitude'].tolist()
	Latitudes  = group['Latitude'].tolist()
	x,y = m(Longitudes,Latitudes)
	m.plot(x,y,marker = 'None',linewidth=1.75,zorder = 100,alpha=1,linestyle='-', color = m_colors[i])
	xi,yi = m(Longitudes[0],Latitudes[0])
	m.scatter(xi,yi,marker = 's',s=100,zorder = 100,alpha=1, color = m_colors[i],label=name)
	i+=1


##add countries
#m.readshapefile('/Volumes/storage/ne_10m_admin_0_countries/ne_10m_admin_0_countries', 'borders', drawbounds = False)
#boundaries = []
#colors = {
#'Canada':'#B1C29B',
#'United States of America':'#7E92BD',
#'Russia':'#D78F84',
#'Denmark':'#E89B6D',
#'Greenland':'#E89B6D',
#'Iceland':'#5AB2C2',
#'Finland':'#6294BC',
#'Sweden':'#FBC759',
#'Norway':'#BB8FAA',
#}
#
#colors = {
#'Canada':					'#deebf7',
#'United States of America':	'#c6dbef',
#'Russia':					'#9ecae1',
#'Denmark':					'#6baed6',
#'Greenland':				'#6baed6',
#'Iceland':					'#4292c6',
#'Finland':					'#2171b5',
#'Sweden':					'#08519c',
#'Norway':					'#08306b',
#}
#
#
#i=0
#for info, shape in zip(m.borders_info, m.borders):    
#    if info['ADMIN'] in ['Russia','Canada','United States of America','Finland','Sweden','Norway','Iceland','Denmark','Greenland']:
#        patch = Polygon(np.array(shape),closed=True,facecolor=colors[info['ADMIN']],edgecolor=colors[info['ADMIN']],alpha=0.75,zorder=1)
#        axes.add_patch(patch)
#        i+=1	

#add arctic circle
arc_circle = []
for lon in np.arange(-180,180):
	lat = 66.56083
	arc_circle.append([lon,lat])
xc,yc = m([row[0] for row in arc_circle],[row[1] for row in arc_circle])
m.plot(xc,yc,marker = 'None', color = 'grey',linewidth=1.5,linestyle='--')

xd,yd = m(0,0)
l = m.scatter(xd,yd,color='w')


handles, labels = axes.get_legend_handles_labels()
plt.legend([l,handles[0],handles[1],handles[2],handles[3],l,l,handles[4],handles[5],handles[6],handles[7],handles[8],handles[9],handles[10],l,l,handles[11],handles[12]],[r'$\bf{Ground}$',labels[0],labels[1],labels[2],labels[3],'',r'$\bf{Aircraft}$',labels[4],labels[5],labels[6],labels[7],labels[8],labels[9],labels[10],'',r'$\bf{Icebreaker}$',labels[11],labels[12]],numpoints=1, scatterpoints=1,loc=2)


os.chdir('/Users/mcallister/projects/INP/Alert_INP2016/bin/prev_measurements/')
plt.savefig('AlertINP_prev_measurements.png', bbox_inches='tight', dpi=300)
plt.show()

