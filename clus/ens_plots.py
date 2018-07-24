#*********************************
#           ens_plots            *
#*********************************

# Standard packages
import os
import sys
from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
#from mpl_toolkits.basemap import Basemap
import math

def ens_plots(dir_OUTPUT,name_outputs,numclus,field_to_plot, ens_mindist, climatology = None, ensemble_mean = None):
    '''
    \nGOAL:
    Plot the chosen field for each ensemble
    NOTE:
    '''

    # User-defined libraries
    import matplotlib.path as mpath
    from read_netcdf import read_N_2Dfields

    # OUTPUT DIRECTORY
    OUTPUTdir=dir_OUTPUT+'OUTPUT/'
    if not os.path.exists(OUTPUTdir):
        os.mkdir(OUTPUTdir)
        print('The output directory {0} is created'.format(OUTPUTdir))
    else:
        print('The output directory {0} already exists'.format(OUTPUTdir))

    tit=field_to_plot
    print('Number of clusters: {0}'.format(numclus))

    print(name_outputs)
    varname=name_outputs.split("_")[0]
    kind=name_outputs.split("_")[5]

    #____________Reading the netCDF file of N 2Dfields of anomalies, saved by ens_anom.py
    ifile=os.path.join(OUTPUTdir,'ens_anomalies_{0}.nc'.format(name_outputs))
    vartoplot, varunits, lat, lon = read_N_2Dfields(ifile)
    print('vartoplot dim: (numens x lat x lon)={0}'.format(vartoplot.shape))
    numens=vartoplot.shape[0]

    if climatology is not None:
        print('Plotting differences with the external climatology instead that with the ensemble mean\n')
        vartoplot = vartoplot + ensemble_mean - climatology


    #____________Load labels
    namef=os.path.join(OUTPUTdir,'labels_{0}.txt'.format(name_outputs))
    labels=np.loadtxt(namef,dtype=int)
    print(labels)

    n_color_levels = 21
    n_levels = 6
    draw_contour_lines = False

    mi = np.percentile(vartoplot, 5)
    ma = np.percentile(vartoplot, 95)
    oko = max(abs(mi), abs(ma))
    clevels = np.linspace(-math.ceil(oko*100)/100, math.ceil(oko*100)/100, n_color_levels)

    # if field_to_plot=='anomalies':
    #     # compute range colorbar for anomalies
    #     delta=0.05
    #     if abs(math.floor(mi*100)/100)<math.ceil(ma*100)/100:
    #         rangecbarmin=-math.ceil(ma*100)/100
    #         rangecbarmax=math.ceil(ma*100)/100+delta
    #     else:
    #         rangecbarmin=math.floor(mi*100)/100
    #         rangecbarmax=abs(math.floor(mi*100)/100)+delta
    # else:
    #     # compute range colorbar for climatologies
    #     delta=0.2
    #     rangecbarmin=math.floor(mi)
    #     rangecbarmax=math.ceil(ma)+delta
    #
    # clevels=np.arange(rangecbarmin,rangecbarmax,delta)
    print('levels', len(clevels), min(clevels), max(clevels))

    #clevels=np.arange(2,44,delta)
    #clevels=np.arange(-0.7,0.75,delta)
    #clevels=np.arange(0,6.2,delta)

    colors=['b','g','r','c','m','y','DarkOrange','grey']

    clat=lat.min()+abs(lat.max()-lat.min())/2
    clon=lon.min()+abs(lon.max()-lon.min())/2

    boundary = np.array([[lat.min(),lon.min()], [lat.max(),lon.min()], [lat.max(),lon.max()], [lat.min(),lon.max()]])
    bound = mpath.Path(boundary)

    #proj = ccrs.Orthographic(central_longitude=clon, central_latitude=clat)

    proj = ccrs.PlateCarree()

    #m = Basemap(projection='cyl',llcrnrlat=min(lat),urcrnrlat=max(lat),llcrnrlon=min(lon),urcrnrlon=max(lon),resolution='c')

    fig = plt.figure(figsize=(24,14))
    for nens in range(numens):
        #print('//////////ENSEMBLE MEMBER {0}'.format(nens))
        ax = plt.subplot(6, 10, nens+1, projection=proj)

        #m.drawcoastlines()
        ax.set_global()
        ax.coastlines()

        # use meshgrid to create 2D arrays
        xi,yi=np.meshgrid(lon,lat)
        #x_i,y_i=np.meshgrid(lon,lat)
        #xi,yi=m(x_i,y_i)

        # Plot Data
        if field_to_plot=='anomalies':
            #map_plot=m.contourf(xi,yi,vartoplot[nens],clevels,cmap=plt.cm.RdBu_r)
            map_plot = ax.contourf(xi,yi,vartoplot[nens],clevels,cmap=plt.cm.RdBu_r, transform = proj, extend = 'both')
        else:
            map_plot = ax.contourf(xi,yi,vartoplot[nens],clevels, transform = proj, extend = 'both')

        #ax.set_boundary(bound, transform = proj)
        latlonlim = [lon.min(), lon.max(), lat.min(), lat.max()]
        ax.set_extent(latlonlim, crs = proj)
        #print('Setting limits: ', latlonlim)

        # proj_to_data = proj._as_mpl_transform(ax) - ax.transData
        # rect_in_target = proj_to_data.transform_path(bound)
        # ax.set_boundary(rect_in_target)

        #print('min={0}'.format(vartoplot[nens].min()))
        #print('max={0}\n'.format(vartoplot[nens].max()))

        # Add Title
        subtit = nens
        title_obj=plt.title(subtit, fontsize=32, fontweight='bold')
        for nclus in range(numclus):
            if nens in np.where(labels==nclus)[0]:
                title_obj.set_backgroundcolor(colors[nclus])

    cax = plt.axes([0.1, 0.03, 0.8, 0.03]) #horizontal
    cb=plt.colorbar(map_plot,cax=cax, orientation='horizontal')#, labelsize=18)
    cb.ax.tick_params(labelsize=18)

    plt.suptitle(kind+' '+varname+' '+tit+' ('+varunits+')', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (2038-2068) JJA 2m temperature '+tit+' (degC)', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (1979-2008) JJA 2m temperature '+tit+' (degC)', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (1979-2008) JJA precipitation rate '+tit+' (mm/day)', fontsize=45, fontweight='bold')

    plt.subplots_adjust(top=0.85)
    top    = 0.89  # the top of the subplots of the figure
    bottom = 0.12    # the bottom of the subplots of the figure
    left   = 0.02    # the left side of the subplots of the figure
    right  = 0.98  # the right side of the subplots of the figure
    hspace = 0.36   # the amount of height reserved for white space between subplots
    wspace = 0.14    # the amount of width reserved for blank space between subplots
    plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

    # plot the selected fields
    namef=os.path.join(OUTPUTdir,'{0}_{1}.eps'.format(field_to_plot,name_outputs))
    fig.savefig(namef)#bbox_inches='tight')
    print('An eps figure for the selected fields is saved in {0}'.format(OUTPUTdir))
    print('____________________________________________________________________________________________________________________')

    plt.ion()
    fig2 = plt.figure(figsize=(16,12))
    print(numclus)
    side1 = int(np.ceil(np.sqrt(numclus)))
    side2 = int(np.ceil(numclus/float(side1)))
    print(side1,side2,numclus)

    for clu in range(numclus):
        #print('//////////ENSEMBLE MEMBER {0}'.format(nens))
        ax = plt.subplot(side1, side2, clu+1, projection=proj)

        ok_ens = ens_mindist[clu][0]

        #m.drawcoastlines()
        ax.set_global()
        ax.coastlines(linewidth = 2)

        # use meshgrid to create 2D arrays
        xi,yi=np.meshgrid(lon,lat)
        #x_i,y_i=np.meshgrid(lon,lat)
        #xi,yi=m(x_i,y_i)

        # Plot Data
        if field_to_plot=='anomalies':
            #map_plot=m.contourf(xi,yi,vartoplot[nens],clevels,cmap=plt.cm.RdBu_r)
            map_plot = ax.contourf(xi,yi,vartoplot[ok_ens],clevels,cmap=plt.cm.RdBu_r, transform = proj, extend = 'both')
            if draw_contour_lines:
                map_plot_lines = ax.contour(xi,yi,vartoplot[ok_ens], n_levels, colors = 'k', transform = proj, linewidth = 0.5)
        else:
            map_plot = ax.contourf(xi,yi,vartoplot[ok_ens],clevels, transform = proj, extend = 'both')
            if draw_contour_lines:
                map_plot_lines = ax.contour(xi,yi,vartoplot[ok_ens], n_levels, colors = 'k', transform = proj, linewidth = 0.5)

        #ax.set_boundary(bound, transform = proj)
        latlonlim = [lon.min(), lon.max(), lat.min(), lat.max()]
        ax.set_extent(latlonlim, crs = proj)
        #print('Setting limits: ', latlonlim)

        # proj_to_data = proj._as_mpl_transform(ax) - ax.transData
        # rect_in_target = proj_to_data.transform_path(bound)
        # ax.set_boundary(rect_in_target)

        #print('min={0}'.format(vartoplot[nens].min()))
        #print('max={0}\n'.format(vartoplot[nens].max()))

        # Add Title
        #title_obj=plt.title('Cluster {} - {} ensembles out of {}'.format(clu, sum(labels == clu), numens), fontsize=20, fontweight='bold')
        title_obj=plt.title('Cluster {} - {:3.0f}% of cases'.format(clu, (100.0*sum(labels == clu))/numens), fontsize=20, fontweight='bold')
        title_obj.set_backgroundcolor(colors[clu])

    cax = plt.axes([0.1, 0.05, 0.8, 0.05]) #horizontal
    cb = plt.colorbar(map_plot,cax=cax, orientation='horizontal')#, labelsize=18)
    cb.ax.tick_params(labelsize=18)

    #plt.suptitle(kind+' '+varname+' '+tit+' ('+varunits+')', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (2038-2068) JJA 2m temperature '+tit+' (degC)', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (1979-2008) JJA 2m temperature '+tit+' (degC)', fontsize=45, fontweight='bold')
    #plt.suptitle(kind+' (1979-2008) JJA precipitation rate '+tit+' (mm/day)', fontsize=45, fontweight='bold')

    #plt.tight_layout()

    # plt.subplots_adjust(top=0.85)
    # top    = 0.89  # the top of the subplots of the figure
    # bottom = 0.12    # the bottom of the subplots of the figure
    # left   = 0.02    # the left side of the subplots of the figure
    # right  = 0.98  # the right side of the subplots of the figure
    # hspace = 0.36   # the amount of height reserved for white space between subplots
    # wspace = 0.14    # the amount of width reserved for blank space between subplots
    # plt.subplots_adjust(left=left, bottom=bottom, right=right, top=top, wspace=wspace, hspace=hspace)

    # plot the selected fields
    namef=os.path.join(OUTPUTdir,'Clusters_{0}_{1}.eps'.format(field_to_plot,name_outputs))
    fig2.savefig(namef)#bbox_inches='tight')

    return


#========================================================

if __name__ == '__main__':
    print('This program is being run by itself')

    print('**************************************************************')
    print('Running {0}'.format(sys.argv[0]))
    print('**************************************************************')
    dir_OUTPUT    = sys.argv[1]          # OUTPUT DIRECTORY
    name_outputs  = sys.argv[2]          # name of the outputs
    numclus       = int(sys.argv[3])  # number of clusters
    field_to_plot = sys.argv[4]          #field to plot ('climatologies', 'anomalies', '75th_percentile', 'mean', 'maximum', 'std', 'trend')

    ens_plots(dir_OUTPUT,name_outputs,numclus,field_to_plot)

else:
    print('ens_plots is being imported from another module')
