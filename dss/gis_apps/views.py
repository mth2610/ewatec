#!/usr/bin/python
# -*- coding: utf8 -*-
## Note that:
## datetime.strptime is a function used to convert  string to datetime type
## .strftime is a method used to convert datetime type to string
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import simplejson
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
import tempfile
import itertools
import psycopg2
from gis_apps import models
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image
from forms import UploadForm
from pyunpack import Archive
import os
import StringIO
import csv
from time import time
from datetime import datetime
import pandas as pd
from gislib import serial_statistics
from gislib import sh2ra
from gislib import multivariate_statistics
from gislib import shp2geojson
from database import ODM
from django.db import connection

dbname = "DEI3"
user = "postgres"
host = "localhost"
port = "5432"
password ="maithang1990"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def get_filepaths(directory):
    """
    This function will generate the file names in a directory
    tree by walking the tree either top-down or bottom-up. For each
    directory in the tree rooted at directory top (including top itself),
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def get_filenamelist(directory):

    filename_list = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for files in os.listdir(directory):
        filename_list.append(files)

    return filename_list # Self-explanatory.

class reading_csv():
    def __init__(self,DataName):
        self.DataName = DataName
    def read(self,init_row=1,init_col=1):
        Array_Data = []

        f = open(self.DataName,'rb')
        csv_data = csv.reader(f)
        Header = next(csv_data)
        n_column = len(Header)
        i = 0
        for row in csv_data:
            i = i + 1
            if i >= (init_row-1):
                float_row = [element for element in row]
                Array_Data.append(float_row[(init_col-1):])
        Array_Data = np.array(Array_Data)
        Array_Data = Array_Data.T
        return Array_Data, Header


def gisbase(request):
    args = {}
    args.update(csrf(request))
    total_maps = []
    total_maps_links = []
    if request.user.is_authenticated():
        USER_NAME = request.user.username
        TEMPORARY_MAP_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_maps')
        LONGLIVED_MAP_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'maps')
        temporary_maps = []
        temporary_maps_links = []
        longlived_maps = []
        longlived_maps_links = []

        try:
            temporary_maps = get_filenamelist(TEMPORARY_MAP_DIR)
            for e in temporary_maps:
                temporary_maps_links.append('/media/user/'+USER_NAME+"/"+'temporary_maps'+"/"+e)
        except:
            pass

        try:
            longlived_maps = get_filenamelist(LONGLIVED_MAP_DIR)
            for e in longlived_maps:
                longlived_maps_links.append('media/user/'+USER_NAME+"/"+'maps'+"/"+e)
        except:
            pass

        total_maps = temporary_maps + longlived_maps
        total_maps_links = temporary_maps_links + longlived_maps_links
    else:
        pass



    args['user_maps'] = zip(total_maps,total_maps_links)

    return render_to_response('gisbase.html',args,context_instance=RequestContext(request))

def province(request):
    from vectorformats.Formats import Django, GeoJSON
    #   Add province
    data = models.province_boundary.objects.all()
    djf = Django.Django(geodjango="geometry", properties = ["id","province"])
    geoj = GeoJSON.GeoJSON()
    provinces = geoj.encode(djf.decode(data))

#    return render_to_response('gisbase.html',args)
    return HttpResponse(provinces)

def update_geojson(request):
    from vectorformats.Formats import Django, GeoJSON
    # Get data from postgres and convert to geojason format
    stations_data = models.stations.objects.all()
    stations_djf = Django.Django(geodjango="geometry", properties = ["id","name"])
    stations_geoj = GeoJSON.GeoJSON()
    stations_geojs_string = stations_geoj.encode(stations_djf.decode(stations_data))


    provinces_data = models.province_boundary.objects.all()
    provinces_djf = Django.Django(geodjango="geometry", properties = ["id","province"])
    provinces_geoj = GeoJSON.GeoJSON()
    provinces_geojs_string = provinces_geoj.encode(provinces_djf.decode(provinces_data))

    landuse_data = models.landuse.objects.all()
    landuse_djf = Django.Django(geodjango="geometry", properties = ["id","code"])
    landuse_geoj = GeoJSON.GeoJSON()
    landuse_geojs_string = landuse_geoj.encode(landuse_djf.decode(landuse_data))

    # Get dir path
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    FILE_DIR = os.path.join(BASE_DIR, 'media/geojson/')


     # Delete all of old geojson file
    file_paths = get_filepaths(FILE_DIR)

    if file_paths != []:
        for element in file_paths:
            os.remove(element)

    ## Write new geojason file

    stations_geojson = open(FILE_DIR+"stations.js", "w")
    stations_geojson.write(stations_geojs_string)
    stations_geojson.close()

    provinces_geojson = open(FILE_DIR+"provinces.js", "w")
    provinces_geojson.write(provinces_geojs_string)
    provinces_geojson.close()

    landuse_geojson = open(FILE_DIR+"landuse.js", "w")
    landuse_geojson.write(landuse_geojs_string)
    landuse_geojson.close()

    args = []
    return HttpResponseRedirect('/gis/basemap')

def stations(request):
    from vectorformats.Formats import Django, GeoJSON
    #   Add province
    data = models.stations.objects.all()
    djf = Django.Django(geodjango="geometry", properties = ["id","name"])
    geoj = GeoJSON.GeoJSON()
    stations = geoj.encode(djf.decode(data))

#    return render_to_response('gisbase.html',args)
    return HttpResponse(stations)

def some_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response

@csrf_exempt
def data_review(request):
    if request.user.is_authenticated():
        args ={}
        args.update(csrf(request))
        id_list = request.POST.getlist('id[]',[0,0,0,0])
        name_list = request.POST.getlist('name[]',[0,0,0,0])
        id_list = list(id_list)
        n = len(id_list)


        # connect with server
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()

        data_dict = {}

        for i in range(n):
            variable_list = []
            starttime_list = []
            endtime_list = []

            data = connection.cursor()
            data.execute('SELECT "VariableName","BeginDateTime","EndDateTime" FROM dbo."SeriesCatalog" WHERE "SiteID" = ' + str(int(id_list[i])))


            data = data.fetchall()

            for element in data:
                variable_list.append((str(element[0]).rstrip()).replace(" ","-"))
                starttime_list.append((element[1]).strftime("%Y-%m-%d %H:%M:%S"))
                endtime_list.append((element[2]).strftime("%Y-%m-%d %H:%M:%S"))

            data_dict.update({id_list[i]:zip(variable_list,starttime_list,endtime_list)})

        id_name_list = zip(id_list,name_list)

        args['id_name_list'] = id_name_list
        args['name_list'] = name_list
        args['id_list'] = id_list
        args['data_dict'] = data_dict


        return render_to_response('data-review.html',args,context_instance=RequestContext(request))
    else:
        url = "/auth/require_login"
        return HttpResponse(url)

#@ensure_csrf_cookie
@csrf_exempt
def data_download(request):
    import zipfile
    # Make a variable id dictonary
    if request.user.is_staff:
        # Do something for staff users.
        selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
        selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
        selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
        selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
        dbConnection = connection
        dbCursor = dbConnection.cursor()

        # Create SiteCode, SiteID,
        siteLib = ODM.createLookupTable(dbCursor,'dbo."Sites"','SiteID','SiteName')

        # Create VariableCode, VariableID libary
        variableLib = ODM.createLookupTable(dbCursor,'dbo."Variables"','VariableName','VariableID')


        n = len(selected_variable)
        url = "/media/download_file" +"/"+str(time()).replace(".","_")+ "_myfile.zip"
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        FILE_DIR = os.path.join(BASE_DIR, 'media/download_file')

        zipfile = zipfile.ZipFile(BASE_DIR + url, "w")

        for i in range(n):
            data = ODM.getDataValue(dbConnection,int(selected_id[i]),
                                    variableLib[selected_variable[i].rstrip().replace('-',' ')],
                                    selected_starttime[i],selected_endtime[i],
                                    requestUser='admin',timeZone='LocalDateTime',dateTimeFormat='%Y-%m-%d %H:%M:%S')
            csv_filename = str(selected_id[i])+"_"+str(siteLib[int(selected_id[i])])\
                           +"_"+str(selected_variable[i].rstrip())+"_"+str(selected_starttime[i])\
                           +"_"+str(selected_endtime[i])+'.csv'

            zipfile.writestr(csv_filename,data.to_csv())

        zipfile.close()
        return HttpResponse(url)

    else:
        url = "/auth/permission_error"
        return HttpResponse(url)
#         Do something for anonymous users.
#        return render_to_response('permission_error.html')
#        return HttpResponseRedirect("/auth/permission_error")

@csrf_exempt
def show_graph(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    selected_variable = selected_variable.replace('-',' ')

    if str(request.POST.get('removeoutlier')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False


    # Create VariableCode, VariableID libary
    dbConnection = connection
    dbCursor = dbConnection.cursor()
    variableLib = ODM.createLookupTable(dbCursor,'dbo."Variables"','VariableName','VariableID')

    data = ODM.getDataValue(dbConnection,int(selected_id),
                            variableLib[selected_variable.rstrip().replace('-',' ')],
                            selected_starttime,selected_endtime,
                            requestUser='admin',timeZone='LocalDateTime',dateTimeFormat='%Y-%m-%d %H:%M:%S')

    # Replace -9999 by np.nan
    data = data.replace(-9999,np.nan)

    # Remove outliers before do stuffs
    if remove_outliers_choices == True:
        data['Value'] = serial_statistics.reject_outliers(data['Value'])

##----------------------------------------------------------**----------------------------------------------------------##
# Look for variable type and unit
    variable = dbConnection.cursor()
    variable_str = 'SELECT "DataType", "VariableUnitsID" FROM dbo."Variables" WHERE "VariableName" = '+"'"+str((selected_variable).rstrip())+"'"
    variable.execute(variable_str)
    dbConnection.commit()

    variable_unit = variable.fetchall()
    variable_type = variable_unit[0][0].rstrip()
    unitid = variable_unit[0][1]
    if variable_type == "Average":
        VariableType = 'mean'
    else:
        VariableType = 'sum'

    unitname = dbConnection.cursor()
    unitname_str = 'SELECT "UnitsName" FROM dbo."Units" WHERE "UnitsID" = ' + str(unitid)
    unitname.execute(unitname_str)
    dbConnection.commit()
    unitname = unitname.fetchall()[0][0].rstrip()

##----------------------------------------------------------**----------------------------------------------------------##

    img = serial_statistics.graph_in_endcode64(data,selected_variable.rstrip(),unitname,linear_regression = False)


    # Set statistical parameters
    args = {}
    datavalue = list(data['Value'])
    args['standard_deviation'] = str(np.nanstd(datavalue))
    args['mean'] = str(np.nanmean(datavalue))
    args['min'] = str(np.nanmin(datavalue))
    args['max'] = str(np.nanmax(datavalue))
    args['cv'] = str(np.nanstd(datavalue)/np.nanmean(datavalue))

    args['id'] = selected_id
    args['variable'] = selected_variable
    args['starttime'] = selected_starttime
    args['endtime'] = selected_endtime
    args['img'] = img
    args['timestep'] = "raw"
    print "test5"

    return render_to_response('blank_statistic.html',RequestContext(request,args))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def resample_data(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    time_step = request.POST.get('timestep')

    if str(request.POST.get('removeOutliers')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False

    if str(request.POST.get('fillingData')) == "True":
        fillingData = True
    else:
        fillingData = False

    if str(request.POST.get('linear_regression')) == "True":
        linear_regression = True
    else:
        linear_regression = False

    ## Get the data
    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
    connection.commit()
    variable_dictonary = {}
    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()
    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})

    data = connection.cursor()


    data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                 +str(int(selected_id)) + ' AND "VariableID" = '\
                 +str(variable_dictonary[(selected_variable).rstrip()])\
                 + ' AND "LocalDateTime" >='\
                 + "'"+str(selected_starttime)+"'"\
                 + ' AND "LocalDateTime" <= '\
                 + "'"+str(selected_endtime) + "'"\
				 + ' ORDER BY "LocalDateTime"'

    data.execute(data_str)
    connection.commit()
    data = data.fetchall()

##----------------------------------------------------------**----------------------------------------------------------##
# Look for variable type and unit
    variable = connection.cursor()
    variable_str = 'SELECT "DataType", "VariableUnitsID" FROM dbo."Variables" WHERE "VariableName" = '+"'"+str((selected_variable).rstrip())+"'"
    variable.execute(variable_str)
    connection.commit()

    variable_unit = variable.fetchall()
    variable_type = variable_unit[0][0].rstrip()
    unitid = variable_unit[0][1]

    if variable_type == "Average":
        VariableType = 'mean'
    else:
        VariableType = 'sum'

    unitname = connection.cursor()
    unitname_str = 'SELECT "UnitsName" FROM dbo."Units" WHERE "UnitsID" = ' + str(unitid)
    unitname.execute(unitname_str)
    connection.commit()
    unitname = unitname.fetchall()[0][0].rstrip()

##----------------------------------------------------------**----------------------------------------------------------##

    t = []
    value = []



    for element in data:
        t.append(element[0])
        value.append(element[1])




    for i in range(len(value)):
        if float(value[i]) == -9999:
            value[i] = np.nan

    if remove_outliers_choices == True:
        value = serial_statistics.reject_outliers(value)

    if str(time_step) != "raw":
        data_object = serial_statistics.serial_statistics(t,value,VariableType)
        resample_data = data_object.resample_data(time_step,fillingData=fillingData)
        graph_img = serial_statistics.graph_in_endcode64(resample_data,
                                                         variable=selected_variable.rstrip(), unit=unitname,
                                                         title="",linear_regression=linear_regression)
        value = resample_data.values
    else:
        data_object = serial_statistics.serial_statistics(t,value,VariableType)
        graph_img = serial_statistics.graph_in_endcode64(data_object.DF,
                                                         variable=selected_variable.rstrip(), unit=unitname,
                                                         title="", linear_regression=linear_regression)


    connection.close()
    args = {}
    args['img'] = graph_img
    args['standard_deviation'] = str(np.nanstd(value))
    args['mean'] = str(np.nanmean(value))
    args['min'] = str(np.nanmin(value))
    args['max'] = str(np.nanmax(value))
    args['cv'] = str(np.nanstd(value)/np.nanmean(value))
    args['timestep'] = str(time_step)
    args['id'] = selected_id
    args['variable'] = selected_variable
    args['starttime'] = selected_starttime
    args['endtime'] = selected_endtime

    return render_to_response('blank_statistic.html',RequestContext(request,args))


@csrf_exempt
@login_required(login_url="/auth/require_login")
def histogram_statistics(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')

    if str(request.POST.get('removeoutlier')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False

    if str(request.POST.get('filldata')) == "True":
        filldata = True
    else:
        filldata = False

    if str(request.POST.get('linear_regression')) == "True":
        linear_regression = True
    else:
        linear_regression = False

    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
    connection.commit()
    variable_dictonary = {}
    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()
    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})

    data = connection.cursor()


    data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                 +str(int(selected_id)) + ' AND "VariableID" = '\
                 +str(variable_dictonary[(selected_variable).rstrip()])\
                 + ' AND "LocalDateTime" >='\
                 + "'"+str(selected_starttime)+"'"\
                 + ' AND "LocalDateTime" <= '\
                 + "'"+str(selected_endtime) + "'"\
				 + ' ORDER BY "LocalDateTime"'

    data.execute(data_str)
    connection.commit()
    data = data.fetchall()

##----------------------------------------------------------**----------------------------------------------------------##
# Look for variable type and unit
    variable = connection.cursor()
    variable_str = 'SELECT "DataType", "VariableUnitsID" FROM dbo."Variables" WHERE "VariableName" = '+"'"+str((selected_variable).rstrip())+"'"
    variable.execute(variable_str)
    connection.commit()

    variable_unit = variable.fetchall()
    variable_type = variable_unit[0][0].rstrip()
    unitid = variable_unit[0][1]

    if variable_type == "Average":
        VariableType = 'mean'
    else:
        VariableType = 'sum'

    unitname = connection.cursor()
    unitname_str = 'SELECT "UnitsName" FROM dbo."Units" WHERE "UnitsID" = ' + str(unitid)
    unitname.execute(unitname_str)
    connection.commit()
    unitname = unitname.fetchall()[0][0].rstrip()

##----------------------------------------------------------**----------------------------------------------------------##
    t = []
    value = []


    for element in data:
        t.append(element[0])
        value.append(element[1])


    for i in range(len(value)):
        if float(value[i]) == -9999:
            value[i] = np.nan


    #    remove outliers
    if remove_outliers_choices == True:
        value = serial_statistics.reject_outliers(value)


    data_object = serial_statistics.serial_statistics(t,value)

    graph_img = data_object.histogram(selected_variable.rstrip(),unitname)

    args = {}
    args['img'] = graph_img
    args['standard_deviation'] = str(np.nanstd(value))
    args['mean'] = str(np.nanmean(value))
    args['min'] = str(np.nanmin(value))
    args['max'] = str(np.nanmax(value))


    return render_to_response('other_blank_statistic.html',RequestContext(request,args))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def averagemonthly_statistics(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    time_step = request.POST.get('timestep')

    if str(request.POST.get('removeOutliers')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False

    if str(request.POST.get('fillingData')) == "True":
        fillingData = True
    else:
        fillingData = False

    if str(request.POST.get('linear_regression')) == "True":
        linear_regression = True
    else:
        linear_regression = False


    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
    connection.commit()
    variable_dictonary = {}
    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()
    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})

    data = connection.cursor()
    data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                 +str(int(selected_id)) + ' AND "VariableID" = '\
                 +str(variable_dictonary[(selected_variable).rstrip()])\
                 + ' AND "LocalDateTime" >='\
                 + "'"+str(selected_starttime)+"'"\
                 + ' AND "LocalDateTime" <= '\
                 + "'"+str(selected_endtime) + "'"\
				 + ' ORDER BY "LocalDateTime"'

    data.execute(data_str)
    connection.commit()
    data = data.fetchall()
##----------------------------------------------------------**----------------------------------------------------------##
##----------------------------------------------------------**----------------------------------------------------------##
# Look for variable type and unit
    variable = connection.cursor()
    variable_str = 'SELECT "DataType", "VariableUnitsID" FROM dbo."Variables" WHERE "VariableName" = '+"'"+str((selected_variable).rstrip())+"'"
    variable.execute(variable_str)
    connection.commit()

    variable_unit = variable.fetchall()
    variable_type = variable_unit[0][0].rstrip()
    unitid = variable_unit[0][1]

    if variable_type == "Average":
        VariableType = 'mean'
    else:
        VariableType = 'sum'

    unitname = connection.cursor()
    unitname_str = 'SELECT "UnitsName" FROM dbo."Units" WHERE "UnitsID" = ' + str(unitid)
    unitname.execute(unitname_str)
    connection.commit()
    unitname = unitname.fetchall()[0][0].rstrip()

##----------------------------------------------------------**----------------------------------------------------------##

##----------------------------------------------------------**----------------------------------------------------------##
    t = []
    value = []


    for element in data:
        t.append(element[0])
        value.append(element[1])


    for i in range(len(value)):
        if float(value[i]) == -9999:
            value[i] = np.nan
##----------------------------------------------------------**--------------------------------------------------------
#    remove outliers
    if remove_outliers_choices == True:
        value = serial_statistics.reject_outliers(value)
##----------------------------------------------------------**----------------------------------------------------------##
## Resample data
    if VariableType == 'sum':
        data_object = serial_statistics.serial_statistics(t,value,VariableType)
        resample_DF = (data_object.resample_data('M',fillingData)).values
        t = (data_object.resample_data('M')).index.values
        value = (data_object.resample_data('M')).values
    else:
        pass
##----------------------------------------------------------**----------------------------------------------------------##
    data_object = serial_statistics.serial_statistics(t,value)
    graph_img = data_object.averagemonthly_statistic(selected_variable.rstrip(),unitname)

    args = {}
    args['img'] = graph_img
    args['standard_deviation'] = str(np.nanstd(value))
    args['mean'] = str(np.nanmean(value))
    args['min'] = str(np.nanmin(value))
    args['max'] = str(np.nanmax(value))

    return render_to_response('other_blank_statistic.html',RequestContext(request,args))
##**********************************************************************************************************************##
## Extract data
@csrf_exempt
def extract_data(request):
    import zipfile
    if request.user.is_staff:
        selected_id = request.POST.get('id')
        selected_variable = request.POST.get('variable')
        selected_starttime = request.POST.get('starttime')
        selected_endtime = request.POST.get('endtime')
        time_step = request.POST.get('timestep')
        remove_outliers_choices = request.POST.get('removeOutliers')
        fillingData = request.POST.get('fillingData')

        print remove_outliers_choices
        print fillingData

        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()

        ## Create variable_dictonary
        variable_dictonary = {}
        variable_data = connection.cursor()
        variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
        connection.commit()
        variable_data = variable_data.fetchall()
        for element in variable_data:
            variable_dictonary.update({(element[0]).rstrip():element[1]})

        ## Create SiteID, SiteName libary

        SiteID_SiteName_lib = {}
        SiteID_SiteName = connection.cursor()
        SiteID_SiteName.execute('SELECT "SiteID", "SiteName" FROM dbo."Sites"')
        connection.commit()
        SiteID_SiteName = SiteID_SiteName.fetchall()

        for element in SiteID_SiteName:
            SiteID_SiteName_lib.update({element[0]:(element[1]).rstrip()})


        ## Select data
        data = connection.cursor()
        data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                     +str(int(selected_id)) + ' AND "VariableID" = '\
                     +str(variable_dictonary[(selected_variable).rstrip()])\
                     + ' AND "LocalDateTime" >='\
                     + "'"+str(selected_starttime)+"'"\
                     + ' AND "LocalDateTime" <= '\
                     + "'"+str(selected_endtime) + "'"\
                     + ' ORDER BY "LocalDateTime"'

        data.execute(data_str)
        connection.commit()
        data = data.fetchall()
    ##----------------------------------------------------------**----------------------------------------------------------##
    # Look for variable type
        variable = connection.cursor()
        variable_str = 'SELECT "DataType" FROM dbo."Variables" WHERE "VariableName" = '+"'"+str((selected_variable).rstrip())+"'"
        variable.execute(variable_str)
        connection.commit()
        variable_type = ((variable.fetchall())[0][0]).rstrip()

        if variable_type == "Average":
            VariableType = 'mean'
        else:
            VariableType = 'sum'
    ##----------------------------------------------------------**----------------------------------------------------------##
        t = []
        value = []



        for element in data:
            t.append(element[0])
            value.append(element[1])


        for i in range(len(value)):
            if float(value[i]) == -9999:
                value[i] = np.nan
    ##----------------------------------------------------------**--------------------------------------------------------
    #    remove outliers
        if remove_outliers_choices == "True":
            value = serial_statistics.reject_outliers(value)



    ##----------------------------------------------------------**----------------------------------------------------------##

    ## Resample data
        print "test1***"
        if time_step!= "raw":
            data_object = serial_statistics.serial_statistics(t,value,VariableType)
            resample_data = data_object.resample_data(time_step,fillingData = fillingData)
            datetime = resample_data.index
            value = resample_data.values
        else:
            data_object = pd.Series(value,t)
            if fillingData == True or fillingData == "True":
                data_object = data_object.fillna(method='pad')
            else:
                pass
            datetime  = data_object.index
            value = data_object.values
    ## Format t

        if time_step == 'AS':
            time_type = "%Y"
        elif time_step == 'M':
            time_type = "%Y-%m"
        elif time_step == 'M':
            time_type = "%Y-%m-%d"
        else:
            time_type = "%Y-%m-%d %H:%M:%S"

        t = []
        for e in datetime:
            t.append((e).strftime(time_type))

    ##----------------------------------------------------------**----------------------------------------------------------##
    ## Witre csv file

        url = "/media/download_file" +"/"+str(time()).replace(".","_")+ "_myfile.zip"
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        FILE_DIR = os.path.join(BASE_DIR, 'media/download_file')
        zipfile = zipfile.ZipFile(BASE_DIR + url, "w")

        data = zip(t,value)

        csv_filename = str(selected_id)+"_"+str(SiteID_SiteName_lib[int(selected_id)])+"_"+str(selected_variable.rstrip())+"_"+str(selected_starttime)+"_"+str(selected_endtime)+'.csv'


        csv_out = StringIO.StringIO()
        #         create the csv writer object.
        mywriter = csv.writer(csv_out)
        mywriter.writerow(["Date","Value"])
        for row in data:
            mywriter.writerow([row[0], row[1]])

        zipfile.writestr(csv_filename,csv_out.getvalue())
        csv_out.close()
        zipfile.close()

        return HttpResponse(url)
    else:
        url = "/auth/permission_error"
        return HttpResponse(url)

##**********************************************************************************************************************##
@csrf_exempt
@login_required(login_url="/auth/require_login")
def statistic_data(request):
  	return render_to_response('data-statistic.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_map(request):
    return render_to_response('uploadmap.html',context_instance=RequestContext(request))


@login_required(login_url="/auth/require_login")
@csrf_exempt
def confirm_upload_map(request):

    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    MAP_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_maps')
    if not os.path.exists(MAP_DIR):
        os.makedirs(MAP_DIR)
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file_name = str(request.FILES['upload_file'])

            # extract .rar or .zip file
            Archive(FILE_DIR+"/"+file_name).extractall(FILE_DIR)
            ## remove .rar or .zip file
            os.remove(FILE_DIR+"/"+file_name)

            shpfile = get_filenamelist(FILE_DIR)
            shpfilename = shpfile[0].replace(shpfile[0][-3:],"shp")

            ## reproject to 3857
            outfilename, outputfiledir = shp2geojson.reprojectshp(shpfilename,FILE_DIR,3857)
            ## convert to geojson
            shp2geojson.shp2geojs(outfilename,outputfiledir, MAP_DIR)

            ## delete all shape file
            for files in get_filepaths(FILE_DIR):
                os.remove(files)

            args = {}
            args.update(csrf(request))

#            return render_to_response('gisbase.html',args,context_instance=RequestContext(request))
            return HttpResponseRedirect('/gis/basemap')
    else:
        form = UploadForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    filename = (request.FILES['filename']).name

    return render_to_response('uploadmap.html',args,context_instance=RequestContext(request))


@csrf_exempt
def export2swat(request):
    from datetime import timedelta
    import zipfile
    import datetime
    if request.user.is_staff:
        args ={}
        args.update(csrf(request))
        id_list = request.POST.getlist('id[]',[0,0,0,0])
        name_list = request.POST.getlist('name[]',[0,0,0,0])
        swat_starttime = request.POST.get('swat_starttime')
        swat_endtime = request.POST.get('swat_endtime')

        id_list = list(id_list)
        n = len(id_list)
        # connect with server
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()

        data_dict = {}

    ##----------------------------------------------------------**----------------------------------------------------------##
    ## Create site varibale dict
        starttime_list = []
        endtime_list = []

        for i in range(n):
            variable_list = []
            data = connection.cursor()
            data.execute('SELECT "VariableName","BeginDateTime","EndDateTime" FROM dbo."SeriesCatalog" WHERE "SiteID" = ' + str(int(id_list[i])))
            data = data.fetchall()

            for element in data:
                variable_list.append((str(element[0]).rstrip()).replace(" ","-"))
                starttime_list.append((element[1]))
                endtime_list.append((element[2]))

            data_dict.update({id_list[i]:variable_list})

        id_name_list = zip(id_list,name_list)
        selected_starttime = min(starttime_list)
        selected_endtime = max(endtime_list)

        ##----------------------------------------------------------**----------------------------------------------------------##
        ## Create variable libary
        variable_dictonary = {}
        variable_data = connection.cursor()
        variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
        connection.commit()
        variable_data = variable_data.fetchall()
        for element in variable_data:
            variable_dictonary.update({(element[0]).rstrip():element[1]})
        ##----------------------------------------------------------**----------------------------------------------------------##
        ## Create time range


        deltatime = timedelta(days=1)
        DATE = []
        i = 0

        if str(swat_starttime).rstrip() != "" and str(swat_endtime).rstrip() != "":
            starttime = datetime.datetime.strptime(str(swat_starttime).rstrip(),"%Y-%m-%d")
            endtime = datetime.datetime.strptime(str(swat_endtime).rstrip(),"%Y-%m-%d")
            datetime = starttime
        else:
            starttime = datetime.datetime(selected_starttime.year,selected_starttime.month,selected_starttime.day)
            endtime =  datetime.datetime(selected_endtime.year,selected_endtime.month,selected_endtime.day)
            datetime = starttime


        while datetime < endtime:
            datetime = starttime + i*deltatime
            DATE.append(datetime)
            i = i + 1

        DF = pd.DataFrame(index=DATE)
        startyear = str(starttime.year)

        if len(str(starttime.month)) > 1:
            startmonth = str(starttime.month)
        else:
            startmonth = "0" + str(starttime.month)

        if len(str(starttime.day)) > 1:
            startday = str(starttime.day)
        else:
            startday = "0" + str(starttime.day)

        outputfile_header = startyear + startmonth + startday


        ##----------------------------------------------------------**----------------------------------------------------------##

        # Create SiteID, SiteName libary

        SiteID_SiteName_lib = {}
        SiteID_SiteName = connection.cursor()
        SiteID_SiteName.execute('SELECT "SiteID", "SiteName","Latitude","Longitude","Elevation_m" FROM dbo."Sites"')
        connection.commit()
        SiteID_SiteName = SiteID_SiteName.fetchall()
        SiteID_XYZ_lib = {}

        for element in SiteID_SiteName:
            SiteID_SiteName_lib.update({element[0]:(element[1]).rstrip()})
            SiteID_XYZ_lib.update({element[0]:[element[3],element[2],element[4]]})


        USER_NAME = request.user.username
        url = "/media/user/" + USER_NAME +"/temporary_files/"+str(time()).replace(".","_")+ "_myfile.zip"
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        FILE_DIR = os.path.join(BASE_DIR, "media/user/" + USER_NAME +"/temporary_files/")
        zipfile = zipfile.ZipFile(BASE_DIR + url, "w")


        RH_location = []
        WS_location = []
        SH_location = []
        RA_location = []
        T_location = []
        RF_location = []

        variable_for_swat = ["Precipitation","Relative Humidity", "Wind speed","Incoming shortwave radiation","Maximum Temperature","Minimum Temperature","Sunny Hour"]

        for site, varibale in data_dict.items():
            T = [[],[]]
            for i in range(len(varibale)):
                varibale_in_loop = str(((str(varibale[i])).rstrip()).replace("-"," "))
                if varibale_in_loop == "Precipitation":
                    csv_filename = "RF_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    RF_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])

                elif varibale_in_loop == "Relative Humidity":
                    csv_filename = "RH_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    RH_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])

                elif varibale_in_loop == "Wind speed":
                    csv_filename = "WS_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    WS_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])

                elif varibale_in_loop == "Incoming shortwave radiation":
                    csv_filename = "RA_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    RA_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])

                elif varibale_in_loop == "Maximum Temperature":
                    csv_filename = "T_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    T_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])

                elif varibale_in_loop == "Sunny Hour":
                    csv_filename = "RA_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                    RA_location.append([csv_filename.replace(".txt","")] + SiteID_XYZ_lib[int(site)])
                else:
                    pass


                if (varibale_in_loop in variable_for_swat) == True:
                    data = connection.cursor()
                    data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                               + str(int(site)) + ' AND "VariableID" = '\
                               + str(variable_dictonary[varibale_in_loop])\
                               + ' AND "LocalDateTime" >='\
                               + "'"+str(selected_starttime.strftime("%Y-%m-%d %H:%M:%S"))+"'"\
                               + ' AND "LocalDateTime" <= '\
                               + "'"+str(selected_endtime.strftime("%Y-%m-%d %H:%M:%S")) + "'"\
                               + ' ORDER BY "LocalDateTime"'
                    data.execute(data_str)
                    connection.commit()
                    data = data.fetchall()
        ##----------------------------------------------------------**----------------------------------------------------------##
                    t = []
                    value = []


                    for element in data:
                        t.append(element[0])
                        value.append(element[1])


                    for i in range(len(value)):
                        if float(value[i]) == -9999:
                            value[i] = np.nan

                        if varibale_in_loop == "Relative Humidity":
                            if value[i] > 1 or value[i] <0:
                                value[i] = np.nan
                        elif varibale_in_loop == "Sunny Hour":
                            if value[i] > 24 or value[i] < 0:
                                value[i] = np.nan
                        else:
                            pass


        ##----------------------------------------------------------**----------------------------------------------------------##

                    if varibale_in_loop == "Wind speed":
                        value = list(np.array(value)*4.87/(math.log(67.8*10 - 5.42)))
                    elif varibale_in_loop == "Sunny Hour":
                        value = list((sh2ra.sh2ra(value,float((SiteID_XYZ_lib[int(site)])[1]),t)).Ra_solar())
                    else:
                        pass

                    if varibale_in_loop == "Precipitation" or varibale_in_loop == "Sunny Hour":

                        variable_type = "sum"
                    else:
                        variable_type = "mean"

                    df = pd.DataFrame({"value":value},index=t)
                    df = df.resample("D",variable_type)
                    final_df = DF.join(df)
                    final_df = final_df.replace(np.nan,-99.0)

                    if varibale_in_loop == "Incoming shortwave radiation":
                        final_value = (final_df.value)*24*60*60/1000000

                    final_value = list(final_df.value)

                    ## Export file
                    if varibale_in_loop == "Maximum Temperature":
                        T[0] = final_value
                    elif varibale_in_loop == "Minimum Temperature":
                        T[1] = final_value
                    else:
                        csv_out = StringIO.StringIO()
                        mywriter = csv.writer(csv_out)
                        mywriter.writerow([outputfile_header])
                        for element in final_value:
                            mywriter.writerow([element])
                        zipfile.writestr(csv_filename,csv_out.getvalue())
                        csv_out.close()


                ## Export file
            if T[0] != [] and T[1] != []:
                csv_filename = "T_" + (SiteID_SiteName_lib[int(site)]).replace(" ","_") +'.txt'
                csv_out = StringIO.StringIO()
                mywriter = csv.writer(csv_out)
                mywriter.writerow([outputfile_header])
                for element in zip(*T):
                    mywriter.writerow(element)
                zipfile.writestr(csv_filename,csv_out.getvalue())
                csv_out.close()


        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create RF_location file
        csv_out = StringIO.StringIO()
        if RF_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in RF_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])

            zipfile.writestr("RF_location.txt",csv_out.getvalue())
            csv_out.close()

        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create RH_location file

        csv_out = StringIO.StringIO()
        if RH_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in RH_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])
            zipfile.writestr("RH_location.txt",csv_out.getvalue())
            csv_out.close()

        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create WS_location file

        csv_out = StringIO.StringIO()
        if WS_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in WS_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])
            zipfile.writestr("WS_location.txt",csv_out.getvalue())
            csv_out.close()


        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create SH_location file


        csv_out = StringIO.StringIO()
        if SH_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in SH_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])
            zipfile.writestr("SH_location.txt",csv_out.getvalue())
            csv_out.close()

        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create RA_location file

        csv_out = StringIO.StringIO()
        if RA_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in RA_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])
            zipfile.writestr("RA_location.txt",csv_out.getvalue())
            csv_out.close()

        ##----------------------------------------------------------**----------------------------------------------------------##
        ## create T_location file

        csv_out = StringIO.StringIO()
        if T_location != []:
            mywriter = csv.writer(csv_out)
            mywriter.writerow(["ID","NAME","LAT","LONG","ELEVATION"])
            i = 0
            for e in T_location:
                i = i + 1
                if e[3] == None:
                    mywriter.writerow([i,e[0],e[2],e[1],"0"])
                else:
                    mywriter.writerow([i,e[0],e[2],e[1],e[3]])
            zipfile.writestr("T_location.txt",csv_out.getvalue())
            csv_out.close()

        zipfile.close()
        return HttpResponse(url)
    else:
        url = "/auth/permission_error"
        return HttpResponse(url)


def get_data(id_list,varibale_list,starttime_list,endtime_list):
    selected_id = id_list
    selected_variable = varibale_list
    selected_starttime = starttime_list
    selected_endtime = endtime_list

    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
    connection.commit()


    ## Create variable libary
    variable_dictonary = {}
    variablename_datatype_dict = {}
    variablename_unitid_dict = {}
    varibalename_variablecode_dict = {}

    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID","DataType","VariableUnitsID","VariableCode" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()

    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})
        variablename_datatype_dict.update({(element[0]).rstrip():(element[2]).rstrip()})
        variablename_unitid_dict.update({(element[0]).rstrip():element[3]})
        varibalename_variablecode_dict.update({(element[0]).rstrip():(element[4]).rstrip()})

    ## Create unit libary
    unitid_unitname_dictonary = {}
    unit_data = connection.cursor()
    unit_data.execute('SELECT "UnitsID","UnitsName","UnitsAbbreviation" FROM dbo."Units"')
    connection.commit()
    unit_data = unit_data.fetchall()

    for element in unit_data:
        unitid_unitname_dictonary.update({element[0]:[(element[1]).rstrip(),[(element[2]).rstrip()]]})


    ## Create SiteID, SiteName libary

    SiteID_SiteName_lib = {}
    SiteID_LatLong_lib = {}
    SiteID_SiteName = connection.cursor()
    SiteID_SiteName.execute('SELECT "SiteID", "SiteName","Latitude","Longitude","Elevation_m" FROM dbo."Sites"')
    connection.commit()
    SiteID_SiteName = SiteID_SiteName.fetchall()

    for element in SiteID_SiteName:
        SiteID_SiteName_lib.update({element[0]:(element[1]).rstrip()})
        SiteID_LatLong_lib.update({element[0]:[element[2],element[3],element[4]]})


    ## get data
    n = len(selected_variable)

    final_data = []
    variable_header = []
    variable_type = []
    unitname = []
    unit_abbr = []

    for i in range(n):
        final_data.append([[],[]])


    for i in range(n):
        data = connection.cursor()
        data_str = 'SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '\
                   + str(int(selected_id[i])) + ' AND "VariableID" = '\
                   + str(variable_dictonary[((selected_variable[i]).rstrip()).replace("-"," ")])\
                   + ' AND "LocalDateTime" >='\
                   + "'"+str(selected_starttime[i])+"'"\
                   + ' AND "LocalDateTime" <= '\
                   + "'"+str(selected_endtime[i]) + "'"\
                   + ' ORDER BY "LocalDateTime"'
        data.execute(data_str)

        connection.commit()
        data = data.fetchall()

        for e in data:
            final_data[i][0].append(e[0])
            final_data[i][1].append(e[1])



        variable_header.append(((selected_variable[i]).rstrip()).replace("-"," "))
        variable_type.append(variablename_datatype_dict[((selected_variable[i]).rstrip()).replace("-"," ")])
        unitname.append(unitid_unitname_dictonary[variablename_unitid_dict[((selected_variable[i]).rstrip()).replace("-"," ")]][0])
        unit_abbr.append(unitid_unitname_dictonary[variablename_unitid_dict[((selected_variable[i]).rstrip()).replace("-"," ")]][1])


    return variable_header,variable_type, final_data, unitname, unit_abbr, SiteID_LatLong_lib, varibalename_variablecode_dict, SiteID_SiteName_lib


@login_required(login_url="/auth/require_login")
def upload_model_file(request):

    return render_to_response('upload_modeled_file.html',context_instance=RequestContext(request))


@login_required(login_url="/auth/require_login")
@csrf_exempt
def confirm_model_file(request):
    from datetime import datetime
    USER_NAME = request.user.username
    FILE_PATH = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files/'+str(request.FILES['upload_file']))
    if  os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

    if request.method == 'POST':

        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file_name = str(request.FILES['upload_file'])


            args = {}
            args['file_path'] = FILE_PATH
            args['id'] = str(request.POST['id'])
            args['variable'] = str(request.POST['variable'])
            args['starttime'] = str(request.POST['starttime'])
            args['endtime'] = str(request.POST['endtime'])
            args.update(csrf(request))

            return render_to_response('compare_with_model.html',args,context_instance=RequestContext(request))
    else:
        form = UploadForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    filename = (request.FILES['filename']).name

    return render_to_response('upload_modeled_file.html',args,context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def validation_analysis(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    time_step = request.POST.get('timestep')
    observation_plot = str(request.POST.get('observation_plot'))
    simulation_plot = str(request.POST.get('simulation_plot'))
    file_path = request.POST.get('file_path')



    if str(request.POST.get('removeoutlier')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False

    ##----------------------------------------------------------**----------------------------------------------------------##
    ## get real data from database
    variable_header,variable_type, ob_data, unitname, unit_abbr, SiteID_LatLong_lib, varibalename_variablecode_dict,SiteID_SiteName_lib = get_data([selected_id],[selected_variable],[selected_starttime],[selected_endtime])
    ob_df = pd.DataFrame({"ob_value":ob_data[0][1]},index=ob_data[0][0])
    ob_df[ob_df == -9999] = np.nan
    ##----------------------------------------------------------**----------------------------------------------------------##
    ## get simulation data from user file
    sm_data, sm_header = (reading_csv(file_path)).read()
    n_row = len(sm_data[0])
    sm_t = []
    model_data = []


    for i in range(n_row):
        sm_t.append(datetime.strptime(str(sm_data[0][i]).rstrip(),"%m/%d/%Y %H:%M:%S"))

        if float(sm_data[1][i]) != -9999:
            model_data.append(float(sm_data[1][i]))
        else:
            model_data.append(np.nan)

    sm_df = pd.DataFrame({"sm_value":model_data},index=sm_t)
    # sm_df = sm_df[min(ob_df.index):max(ob_df.index)]
    ##----------------------------------------------------------**----------------------------------------------------------##
    ## resample data and join

    if (variable_type[0]).rstrip() == "Cumulative":
        variable_type = "sum"
    else:
        variable_type = "mean"
    ob_df = ob_df.resample(str(time_step),variable_type)
    sm_df = sm_df.resample(str(time_step),variable_type)

    final_df = sm_df.join(ob_df)
    cal_obj = serial_statistics.calibration_validation(final_df,simulation_plot,observation_plot,sm_color="b",ob_color="r",variablename = variable_header[0],unit=unitname[0])
    timeseries_img = cal_obj.timeseries_plot()
    scatter_img = cal_obj.scatter_plot()

    parameter_dict = cal_obj.statistical_parameters()
    args = {}
    args['timeseries_img'] = timeseries_img
    args['scatter_img'] = scatter_img

    args['min_sm'] = str(parameter_dict['min_sm'])
    args['max_sm'] = str(parameter_dict['max_sm'])
    args['mean_sm'] = str(parameter_dict['mean_sm'])
    args['median_sm'] = str(parameter_dict['median_sm'])
    args['std_sm'] = str(parameter_dict['std_sm'])
    args['cv_sm'] = str(parameter_dict['cv_sm'])

    args['min_ob'] = str(parameter_dict['min_ob'])
    args['max_ob'] = str(parameter_dict['max_ob'])
    args['mean_ob'] = str(parameter_dict['mean_ob'])
    args['median_ob'] = str(parameter_dict['median_ob'])
    args['std_ob'] = str(parameter_dict['std_ob'])
    args['cv_ob'] = str(parameter_dict['cv_ob'])

    args['pearson_r'] = str(parameter_dict['pearson_r'])
    args['pearson_p'] = str(parameter_dict['pearson_p'])
    args['pearson_p'] = str(parameter_dict['pearson_p'])
    args['spearman_r'] = str(parameter_dict['spearman_r'])
    args['spearman_p'] = str(parameter_dict['spearman_p'])
    args['nash'] = str(parameter_dict['nash'])

    return render_to_response('validation_analysis.html',args,context_instance=RequestContext(request))

def validation_residual_analysis(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    time_step = request.POST.get('timestep')
    observation_plot = str(request.POST.get('observation_plot'))
    simulation_plot = str(request.POST.get('simulation_plot'))
    file_path = request.POST.get('file_path')

    if str(request.POST.get('removeoutlier')) == "True":
        remove_outliers_choices = True
    else:
        remove_outliers_choices = False
    ##----------------------------------------------------------**----------------------------------------------------------##
    ## get real data from database
    variable_header,variable_type, ob_data, unitname, unit_abbr, SiteID_LatLong_lib, varibalename_variablecode_dict,SiteID_SiteName_lib = get_data([selected_id],[selected_variable],[selected_starttime],[selected_endtime])
    ob_df = pd.DataFrame({"ob_value":ob_data[0][1]},index=ob_data[0][0])
    ob_df[ob_df == -9999] = np.nan
    ##----------------------------------------------------------**----------------------------------------------------------##
    ## get simulation data from user file
    sm_data, sm_header = (reading_csv(file_path)).read()
    n_row = len(sm_data[0])
    sm_t = []
    model_data = []
    for i in range(n_row):
        sm_t.append(datetime.strptime(str(sm_data[0][i]).rstrip(),"%m/%d/%Y %H:%M:%S"))

        if float(sm_data[1][i]) != -9999:
            model_data.append(float(sm_data[1][i]))
        else:
            model_data.append(np.nan)

    sm_df = pd.DataFrame({"sm_value":model_data},index=sm_t)
    ##----------------------------------------------------------**----------------------------------------------------------##
    ## resample data and join

    if (variable_type[0]).rstrip() == "Cumulative":
        variable_type = "sum"
    else:
        variable_type = "mean"
    ob_df = ob_df.resample(str(time_step),variable_type)
    sm_df = sm_df.resample(str(time_step),variable_type)

    final_df = sm_df.join(ob_df)

    cal_obj = serial_statistics.calibration_validation(final_df,simulation_plot,observation_plot,sm_color="b",ob_color="r",variablename = variable_header[0],unit=unitname[0])
    residual_img = cal_obj.residual_analysis()
    args = {}
    args['residual_img'] = residual_img

    return render_to_response('validation_analysis.html',args,context_instance=RequestContext(request))


def blank(request):
    return render_to_response('blank.html',context_instance=RequestContext(request))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def multivariable_statistic(request):
    if len(list(request.POST.getlist('selected_id[]',[0,0,0,0]))) >= 2:
        selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
        selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
        selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
        selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
        selected_sitename = request.POST.getlist('selected_sitename[]',[0,0,0,0])


        data_list = zip(selected_id,selected_variable,selected_starttime,selected_endtime,selected_sitename)
        args = {}
        args['data_list'] = data_list
        return render_to_response('multivariable_statistic.html',RequestContext(request,args))
    else:
        return render_to_response('blank.html',context_instance=RequestContext(request))


def general_multivariable_statistic(request):
    from datetime import datetime
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
    remove_outliers_choices = request.POST.getlist('removeoutlier[]',[0,0,0,0])
    fillingdata = request.POST.getlist('fillingData[]',[0,0,0,0])
    timestep = request.POST.get('timestep')

    for i in range(len(remove_outliers_choices)):
        if str(remove_outliers_choices[i]) == "True":
            remove_outliers_choices[i] = True
        else:
            remove_outliers_choices[i] = False

    selected_variable = [ e.replace("-"," ") for e in selected_variable]


    variable_header,variable_type, datavalue, unitname, unit_abbr, SiteID_LatLong_lib, variablecode_dict, SiteID_SiteName_lib = get_data(selected_id,selected_variable,selected_starttime,selected_endtime)

    selected_starttime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_starttime]
    selected_endtime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_endtime]

    starttime = datetime(min(selected_starttime).year,min(selected_starttime).month,min(selected_starttime).day,0,0,0)
    endtime = datetime(max(selected_endtime).year,max(selected_endtime).month,max(selected_endtime).day,0,0,0)

    time_range = pd.date_range(starttime,endtime,freq = timestep)

    final_df = pd.DataFrame(index=time_range)

    variable = []

    if len(set(selected_id)) != 1:
        for i in range(len(variable_header)):
            variable.append(variablecode_dict[variable_header[i]] + " ("+ str(selected_id[i])+")")
    else:
        for i in range(len(variable_header)):
            variable.append(variablecode_dict[variable_header[i]])


    for i in range(len(datavalue)):
        t = datavalue[i][0]

        value = datavalue[i][1]

        for j in range(len(value)):
            if value[j] == -9999:
                value[j] = np.nan
            else:
                pass

        if remove_outliers_choices[i] == True:
            value = serial_statistics.reject_outliers(value)

        df = pd.DataFrame({str(variable[i]):value},index=t)


        if (variable_type[i]).rstrip() == "Average":
            temp_variable_type = "mean"
        else:
            temp_variable_type = "sum"


        df = df.resample(str(timestep),how =temp_variable_type)

        if fillingdata[i] == True or fillingdata[i] == "True":
            df = df.fillna(method='pad')
        else:
            pass


        final_df = final_df.join(df)
        del df
        del t
        del value
        del temp_variable_type


    mulvariate_obj = multivariate_statistics.general_statistic(final_df)
    scatter_img = mulvariate_obj.scatter_plot()
    timeseries_img = mulvariate_obj.multi_timeserise_plot()
    args = {}
    args['timeseries_img'] = timeseries_img
    args['scatter_img'] = scatter_img

    return render_to_response('blank_multivariable_statistic.html',args,context_instance=RequestContext(request))


def generate_swat_wgn(request):
    import zipfile
    from datetime import datetime
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
    remove_outliers_choices = request.POST.getlist('removeoutlier[]',[0,0,0,0])



#    user_starttime = request.POST.get('user_starttime')
#    user_endtime = request.POST.get('user_endtime')
    for i in range(len(remove_outliers_choices)):
        if str(remove_outliers_choices[i]) == "True":
            remove_outliers_choices[i] = True
        else:
            remove_outliers_choices[i] = False


    user_starttime = []
    user_endtime = []

    if user_starttime != [] and user_endtime != []:
        selected_starttime = [ user_starttime for i in range(len(selected_id))]
        selected_endtime = [ user_endtime for i in range(len(selected_id))]

    variable_header,variable_type, datavalue, unitname, unit_abbr, SiteID_LatLong_lib, varibalename_variablecode_dict,SiteID_SiteName_lib = get_data(selected_id,selected_variable,selected_starttime,selected_endtime)

    variable_for_swat = ["Precipitation","Relative Humidity", "Wind speed","Incoming shortwave radiation","Maximum Temperature","Minimum Temperature","Sunny Hour"]

    data_dict = dict(zip(variable_header,datavalue))

    ## Handle maximum temperure data
    # TMPMX Average maximum air temperature for month
    # TMPSTDMX Standard deviation for maximum air temperature in month

    TMPMX = ["","","","","","","","","","","",""]
    TMPSTDMX = ["","","","","","","","","","","",""]

    try:
        Tmax_DF = pd.DataFrame({"Maximum Temperature":data_dict["Maximum Temperature"][1]}, index = data_dict["Maximum Temperature"][0])
        Tmax_DF[Tmax_DF== -9999] = np.nan

        for i in range(12):
            Tmax_month = (Tmax_DF.index.month)
            TMPMX[i] = np.nanmean(np.array(Tmax_DF[Tmax_month == i + 1]))
            TMPSTDMX[i] = np.nanstd(np.array(Tmax_DF[Tmax_month == i + 1]),ddof=1)

    except:
        pass


    ## Handle minimum temperure data
    # TMPMN Average minimum air temperature for month
    # TMPSTDMN Standard deviation for minimum air temperature in month

    TMPMN = ["","","","","","","","","","","",""]
    TMPSTDMN = ["","","","","","","","","","","",""]

    try:
        Tmin_DF = pd.DataFrame({"Minimum Temperature":data_dict["Minimum Temperature"][1]}, index = data_dict["Minimum Temperature"][0])
        Tmin_DF[Tmin_DF== -9999] = np.nan


        for i in range(12):
            Tmin_month = (Tmin_DF.index.month)
            TMPMN[i] = np.nanmean(np.array(Tmin_DF[Tmin_month == i + 1]))
            TMPSTDMN[i] = np.nanstd(np.array(Tmin_DF[Tmin_month == i + 1]),ddof=1)
    except:
        pass

    ## Handle rainfall  data
    #PCPMM Average amount of precipitation falling in month.
    #PCPSTD Standard deviation for daily precipitation in month.
    #PCPSKW Skew coefficient for daily precipitation in month.
    #PR_W1 Probability of a wet day following a dry day in the month.
    #PR_W2 Probability of a wet day following a wet day in the month.
    #PCPD Average number of days of precipitation in month.
    #RAINHHMX Maximum 0.5 hour rainfall in entire period of record for month.

    PCPMM = ["","","","","","","","","","","",""]
    PCPSTD = ["","","","","","","","","","","",""]
    PCPSKW = ["","","","","","","","","","","",""]
    PR_W1 = ["","","","","","","","","","","",""]
    PR_W2 = ["","","","","","","","","","","",""]
    PCPD = ["","","","","","","","","","","",""]
    RAINHHMX = ["","","","","","","","","","","",""]



    try:
        RF_DF = pd.DataFrame({"Precipitation":data_dict["Precipitation"][1]}, index = data_dict["Precipitation"][0])
        RF_DF[RF_DF == -9999] = np.nan
        daily_RF_DF = RF_DF.resample("D", how = "sum")
        monthly_RF_DF = RF_DF.resample("M", how = "sum")
        daily_RF_DF = daily_RF_DF.dropna()

        daily_value = list(daily_RF_DF["Precipitation"])

        wet_day = [ e > 0 for e in daily_value ]


        wetday_dryday = [True]
        wetday_wetday = [False]

        for i in range(1,len(daily_value)):
            if daily_value[i] > 0 and daily_value[i-1] == 0:
                wetday_dryday.append(True)
                wetday_wetday.append(False)
            elif daily_value[i] > 0 and daily_value[i-1] > 0:
                wetday_dryday.append(False)
                wetday_wetday.append(True)
            else:
                wetday_dryday.append(False)
                wetday_wetday.append(False)


        wet_day_df = pd.DataFrame({"wet_day":wet_day}, index = daily_RF_DF.index)
        wetday_dryday_df = pd.DataFrame({"wetday_dryday":wetday_dryday},index = daily_RF_DF.index)
        wetday_wetday_df = pd.DataFrame({"wetday_wetday":wetday_wetday},index = daily_RF_DF.index)

        num_monthly_wetday_wetday_df = pd.DataFrame({"wetday":wet_day},index = daily_RF_DF.index).resample("M", how = "sum")

        ## Find minimum timestep in data

        datetime = RF_DF.index

        gradient_datetime = []
        for i in range(len(datetime)-1):
            delta = datetime[i+1] - datetime[i]
            gradient_datetime.append(24*60*delta.days + 60*delta.hours + delta.minutes)

        gradient_datetime.append(gradient_datetime[-1])


        if min(gradient_datetime) <= 60:
            index = [ e <= 60 for e in gradient_datetime]

            RAINHHMX_df = RF_DF[index]
            RAINHHMX_df.resample('H',how = "sum")


            if ((max(RAINHHMX_df.index) - min(RAINHHMX_df.index)).days)/365 >= 5:
                for i in range(12):
                    RAINHHMX_month = (RAINHHMX_df.index.month)
                    RAINHHMX[i] = np.nanmax(np.array(RAINHHMX_df[RAINHHMX_month == i + 1]))/2
            else:
                RAINHHMX_df = daily_RF_DF
                for i in range(12):
                    RAINHHMX_month = (RAINHHMX_df.index.month)
                    RAINHHMX[i] = np.nanmax(np.array(RAINHHMX_df[RAINHHMX_month == i + 1]))/3
        else:
            RAINHHMX_df = daily_RF_DF
            for i in range(12):
                RAINHHMX_month = (RAINHHMX_df.index.month)
                RAINHHMX[i] = np.nanmax(np.array(RAINHHMX_df[RAINHHMX_month == i + 1]))/3

        start_RAINHHMX = min(RAINHHMX_df.index)
        end_RAINHHMX = max(RAINHHMX_df.index)
        RAIN_YRS = ((end_RAINHHMX - start_RAINHHMX).days)/365

        for i in range(12):
            RF_month = (monthly_RF_DF.index.month)
            rf_mean = np.nanmean(np.array(monthly_RF_DF[RF_month == i + 1]["Precipitation"]))
            rf_std = np.nanstd(np.array(monthly_RF_DF[RF_month == i + 1]["Precipitation"]),ddof=1)
            PCPMM[i] = rf_mean


            daily_RF_moth = (daily_RF_DF.index.month)
            daily_data = np.array(daily_RF_DF[daily_RF_moth == i + 1]["Precipitation"])

            N = len(daily_data)

            PCPSTD[i] = np.nanstd(daily_data)

            PCPSKW[i] = (N*np.nansum((daily_data - np.mean(daily_data))**3))/((N-1)*(N-2)*(np.nanstd(daily_data,ddof=1)**3))


            number_of_wetday = float((list(wet_day_df[daily_RF_moth == i + 1]["wet_day"])).count(True))
            number_of_dryday = float((list(wet_day_df[daily_RF_moth == i + 1]["wet_day"])).count(False))
            PR_W1[i] = ((list(wetday_dryday_df[daily_RF_moth == i + 1]["wetday_dryday"])).count(True))/number_of_dryday
            PR_W2[i] = ((list(wetday_wetday_df[daily_RF_moth == i + 1]["wetday_wetday"])).count(True))/number_of_wetday

            PCPD[i] = np.nanmean(np.array(num_monthly_wetday_wetday_df[RF_month == i + 1]["wetday"]))

    except:
        pass

    ## Handle sunny hours data

    SOLARAV = ["","","","","","","","","","","",""]
    try:
        try:
            Solar_DF = pd.DataFrame({"Incoming shortwave radiation":data_dict["Incoming shortwave radiation"][1]}, index = data_dict["Incoming shortwave radiation"][0])
            Solar_DF[Solar_DF == -9999] = np.nan
            Solar_DF = Solar_DF.resample('D','mean')

        except:
            SH_DF = pd.DataFrame({"Sunny Hour":data_dict["Sunny Hour"][1]}, index = data_dict["Sunny Hour"][0])
            SH_DF[SH_DF == -9999] = np.nan
            SH_DF = SH_DF.resample('D','sum')

            SiteID_LatLong_lib[int(selected_id[0])][0]
            solar_data = (sh2ra.sh2ra(np.array(SH_DF["Sunny Hour"]),SiteID_LatLong_lib[int(selected_id[0])][0],SH_DF.index)).Ra_solar()

            Solar_DF = pd.DataFrame({"Ra":solar_data},index = SH_DF.index)

        for i in range(12):
            ra_month = (Solar_DF.index.month)
            SOLARAV[i] = np.nanmean(np.array(Solar_DF[ra_month == i + 1]))
    except:
        pass


    ## Calculating dew poitn temperture
    DEWPT = ["","","","","","","","","","","",""]

    try:
        RH_DF = pd.DataFrame({"Relative Humidity":data_dict["Relative Humidity"][1]}, index = data_dict["Relative Humidity"][0])
        RH_DF[RH_DF == -9999] = np.nan
        RH_DF[RH_DF > 1] = np.nan
        RH_DF[RH_DF < 0] = np.nan

        DEW_DF = (Tmax_DF.join(Tmin_DF)).join(RH_DF)
        DEW_DF = DEW_DF.dropna()
        avg_temp = (np.array(DEW_DF["Minimum Temperature"]) + np.array(DEW_DF["Maximum Temperature"]))/2
        e_mon = (np.e)**(np.array(DEW_DF["Relative Humidity"])*((16.78*avg_temp - 116.9)/(avg_temp + 237.3)))

        dew = (237.3*np.log(e_mon) + 116.9)/(16.78 - np.log(e_mon))
        final_dew_df = pd.DataFrame({"DEW":dew},DEW_DF.index)
        for i in range(12):
            dew_month = (final_dew_df.index.month)
            DEWPT[i] = np.mean(np.array(final_dew_df[dew_month == i + 1]))
    except:
        pass

    ## Handle wind speed data

    WNDAV = ["","","","","","","","","","","",""]
    try:
        wind_at_10m = np.array(data_dict["Wind speed"][1])
        wind_at_10m[wind_at_10m == -9999] = np.nan
        wind_at_2m = wind_at_10m*4.87/(math.log(67.8*10 - 5.42))
        WS_DF = pd.DataFrame({"Wind speed":wind_at_2m}, index = data_dict["Wind speed"][0])
        WS_DF[WS_DF == -9999] = np.nan

        for i in range(12):
            ws_month = (WS_DF.index.month)
            WNDAV[i] = np.nanmean(np.array(WS_DF[ws_month == i + 1]))
    except:
        pass



    USER_NAME = request.user.username
    url = "/media/user/" + USER_NAME +"/temporary_files/"+str(time()).replace(".","_")+ "_myfile.zip"
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    FILE_DIR = os.path.join(BASE_DIR, "media/user/" + USER_NAME +"/temporary_files/")
    zipfile = zipfile.ZipFile(BASE_DIR + url, "w")


    csv_out = StringIO.StringIO()
    mywriter = csv.writer(csv_out)


    mywriter.writerow(["OBJECTID",""])
    mywriter.writerow(["STATION",str(selected_id[0])])
    mywriter.writerow(["WLATITUDE",SiteID_LatLong_lib[int(selected_id[0])][0] ])
    mywriter.writerow(["WLONGITUDE",SiteID_LatLong_lib[int(selected_id[0])][1]])

    try:
        mywriter.writerow(["WELEV", SiteID_LatLong_lib[int(selected_id[0])][2] ])
    except:
        mywriter.writerow(["WELEV", ""])

    mywriter.writerow(["RAIN_YRS",RAIN_YRS])



    # TMPMX

    for i in range(12):
        mywriter.writerow(["TMPMX" + str(i+1),TMPMX[i]])


    # TMPMN
    for i in range(12):
        mywriter.writerow(["TMPMN" + str(i+1),TMPMN[i]])


    # TMPSTDMX
    for i in range(12):
        mywriter.writerow(["TMPSTDMX" + str(i+1),TMPSTDMX[i]])



    # TMPSTDMN
    for i in range(12):
        mywriter.writerow(["TMPSTDMN" + str(i+1),TMPSTDMN[i]])

    # PCPMM
    for i in range(12):
        mywriter.writerow(["PCPMM" + str(i+1),PCPMM[i]])


    # PCPSTD
    for i in range(12):
        mywriter.writerow(["PCPSTD" + str(i+1),PCPSTD[i]])



    # PCPSKW
    for i in range(12):
        mywriter.writerow(["PCPSKW" + str(i+1),PCPSKW[i]])

    # PR_W1
    for i in range(12):
        mywriter.writerow(["PR_W1_" + str(i+1),PR_W1[i]])


    # PR_W2
    for i in range(12):
        mywriter.writerow(["PR_W2_" + str(i+1),PR_W2[i]])


    # PCPD
    for i in range(12):
        mywriter.writerow(["PCPD" + str(i+1),PCPD[i]])


    # RAINHHMX
    for i in range(12):
        mywriter.writerow(["RAINHHMX" + str(i+1),RAINHHMX[i]])


    # SOLARAV
    for i in range(12):
        mywriter.writerow(["SOLARAV" + str(i+1),SOLARAV[i]])


    # DEWPT
    for i in range(12):
        mywriter.writerow(["DEWPT" + str(i+1),DEWPT[i]])



    # WNDAV
    for i in range(12):
        mywriter.writerow(["WNDAV" + str(i+1),WNDAV[i]])



    zipfile.writestr("wgn.csv",csv_out.getvalue())
    csv_out.close()
    zipfile.close()


    return HttpResponse(url)

def multiLinearRegression(request):
    from datetime import datetime
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
    remove_outliers_choices = request.POST.getlist('removeoutlier[]',[0,0,0,0])
    timestep = request.POST.get('timestep')
    dependentVariable = request.POST.get('dependentVariable')
    fillingdata = request.POST.getlist('fillingData[]',[0,0,0,0])

    for i in range(len(remove_outliers_choices)):
        if str(remove_outliers_choices[i]) == "True":
            remove_outliers_choices[i] = True
        else:
            remove_outliers_choices[i] = False

    selected_variable = [ e.replace("-"," ") for e in selected_variable]


    variable_header,variable_type, datavalue, unitname, unit_abbr, SiteID_LatLong_lib, variablecode_dict, SiteID_SiteName_lib= get_data(selected_id,selected_variable,selected_starttime,selected_endtime)


    selected_starttime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_starttime]
    selected_endtime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_endtime]

    starttime = datetime(min(selected_starttime).year,min(selected_starttime).month,min(selected_starttime).day,0,0,0)
    endtime = datetime(max(selected_endtime).year,max(selected_endtime).month,max(selected_endtime).day,0,0,0)

    time_range = pd.date_range(starttime,endtime,freq = timestep)

    final_df = pd.DataFrame(index=time_range)

    variable = []

    if len(set(selected_id)) != 1:
        for i in range(len(variable_header)):
            variable.append(variablecode_dict[variable_header[i]] + " ("+ str(selected_id[i])+")")
    else:
        for i in range(len(variable_header)):
            variable.append(variablecode_dict[variable_header[i]])


    for i in range(len(datavalue)):
        t = datavalue[i][0]

        value = datavalue[i][1]

        for j in range(len(value)):
            if value[j] == -9999:
                value[j] = np.nan
            else:
                pass

        if remove_outliers_choices[i] == True:
            value = serial_statistics.reject_outliers(value)

        df = pd.DataFrame({str(variable[i]):value},index=t)


        if (variable_type[i]).rstrip() == "Average":
            temp_variable_type = "mean"
        else:
            temp_variable_type = "sum"


        df = df.resample(str(timestep),how =temp_variable_type)

        if fillingdata[i] == True or fillingdata[i] == "True":
            df = df.fillna(method='pad')
        else:
            pass


        final_df = final_df.join(df)
        del df
        del t
        del value
        del temp_variable_type


    dependentVariable = dependentVariable.split(",")
    sitename = SiteID_SiteName_lib[int(dependentVariable[0])]
    dependentVariableName = (dependentVariable[1]).replace("-"," ")

    dependentVariable = variablecode_dict[(dependentVariable[1]).replace("-"," ")] + " (%s)"%(dependentVariable[0])
    mulvariate_obj = multivariate_statistics.LinearRegression(final_df,dependentVariable)
    predictedValues = mulvariate_obj.predictedValues()
    predictedValues[predictedValues==np.nan] = -9999

    predictedValuesPlot = mulvariate_obj.predictedPlot(variable = dependentVariableName, unit = dict(zip(variable_header,unitname))[dependentVariableName], title = sitename)

    USER_NAME = request.user.username
    csvFileName = "%s_%s_%s.csv"%(str(time()).replace(".","_"),"predicted",dependentVariable.replace(" ","_"))
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    FILE_DIR = os.path.join(BASE_DIR, "media/user/" + USER_NAME +"/temporary_files/"+csvFileName)



    ## open a file for writing.
    csv_out = open(FILE_DIR, 'wb')
    ## create the csv writer object.
    mywriter = csv.writer(csv_out)
    ##print Result
    mywriter.writerow(["DateTime","Values"])

    for row in zip([(pd.to_datetime(e)).strftime("%Y-%m-%d %H:%M:%S") for e in mulvariate_obj.index],predictedValues):
        mywriter.writerow(row)
    csv_out.close()


    args = {}
    args['predictedValues'] = predictedValuesPlot
    args['standard_deviation'] = str(np.nanstd(predictedValues))
    args['mean'] = str(np.nanmean(predictedValues))
    args['min'] = str(np.nanmin(predictedValues))
    args['max'] = str(np.nanmax(predictedValues))
    args['cv'] = str(100*np.nanstd(predictedValues)/np.nanmean(predictedValues))
    args['fileSource'] = "/media/user/" + USER_NAME +"/temporary_files/"+csvFileName
    return render_to_response('linearRegression.html',args,context_instance=RequestContext(request))


def multipleBoxPlot(request):
    from datetime import datetime
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
    remove_outliers_choices = request.POST.getlist('removeoutlier[]',[0,0,0,0])
    timestep = request.POST.get('timestep')
    dependentVariable = request.POST.get('dependentVariable')
    fillingdata = request.POST.getlist('fillingData[]',[0,0,0,0])

    for i in range(len(remove_outliers_choices)):
        if str(remove_outliers_choices[i]) == "True":
            remove_outliers_choices[i] = True
        else:
            remove_outliers_choices[i] = False

    selected_variable = [ e.replace("-"," ") for e in selected_variable]


    variable_header,variable_type, datavalue, unitname, unit_abbr, SiteID_LatLong_lib, variablecode_dict, SiteID_SiteName_lib= get_data(selected_id,selected_variable,selected_starttime,selected_endtime)


    selected_starttime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_starttime]
    selected_endtime = [ datetime.strptime(e,("%Y-%m-%d %H:%M:%S")) for e in selected_endtime]

    starttime = datetime(min(selected_starttime).year,min(selected_starttime).month,min(selected_starttime).day,0,0,0)
    endtime = datetime(max(selected_endtime).year,max(selected_endtime).month,max(selected_endtime).day,0,0,0)

    time_range = pd.date_range(starttime,endtime,freq = timestep)

    final_df = pd.DataFrame(index=time_range)

    variable = []

    for i in range(len(selected_id)):
        variable.append(SiteID_SiteName_lib[int(selected_id[i])])

    for i in range(len(datavalue)):
        t = datavalue[i][0]

        value = datavalue[i][1]

        for j in range(len(value)):
            if value[j] == -9999:
                value[j] = np.nan
            else:
                pass

        if remove_outliers_choices[i] == True:
            value = serial_statistics.reject_outliers(value)

        df = pd.DataFrame({str(variable[i]):value},index=t)


        if (variable_type[i]).rstrip() == "Average":
            temp_variable_type = "mean"
        else:
            temp_variable_type = "sum"


        df = df.resample(str(timestep),how =temp_variable_type)

        if fillingdata[i] == True or fillingdata[i] == "True":
            df = df.fillna(method='pad')
        else:
            pass


        final_df = final_df.join(df)
        del df
        del t
        del value
        del temp_variable_type

    img = multivariate_statistics.multipleBoxPlot(final_df,variable = variablecode_dict[variable_header[0]],unit = unitname[0])
    args = {}
    args['img'] = img

    return render_to_response('multipleBoxPlot.html',args,context_instance=RequestContext(request))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def outlierDectection(request):
    selected_id = request.POST.get('id')
    selected_variable = request.POST.get('variable')
    selected_starttime = request.POST.get('starttime')
    selected_endtime = request.POST.get('endtime')
    outliersDetectionMethod = request.POST.get('outliersDetectionMethod')


    selected_variable = selected_variable.replace("-"," ")
    variable_header,variable_type, ogriData, unitname, unit_abbr, SiteID_LatLong_lib, varibalename_variablecode_dict,SiteID_SiteName_lib = get_data([selected_id],[selected_variable],[selected_starttime],[selected_endtime])
    ogriDF = pd.DataFrame({selected_variable:ogriData[0][1]},index=ogriData[0][0])
    ogriDF[ogriDF == -9999] = np.nan

    outlierObj = serial_statistics.DetectOuliers(ogriDF)

    if outliersDetectionMethod == 'medianFilter':
        filteredData = outlierObj.medianFilter()
    elif outliersDetectionMethod == 'nonParametricMethod':
        filteredData = outlierObj.nonParametricMethod()

    detectedOutlierPlot = outlierObj.outlierDetectionPlot(filteredData,selected_variable,unitname[0])

    exportDf = filteredData[filteredData["outlier"] == True][selected_variable]



    exportData = zip([(pd.to_datetime(e)).strftime("%Y-%m-%d %H:%M:%S") for e in list(exportDf.index.values)],list(exportDf.values))


    args = {}
    args['detectedOutlierPlot'] = detectedOutlierPlot
    args['outliers'] = exportData

    return render_to_response('outlierDetection.html',args,context_instance=RequestContext(request))
