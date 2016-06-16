#!/usr/bin/python
# -*- coding: utf8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from forms import UploadForm
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import os
import simplejson
import itertools
import tempfile
import psycopg2
import csv
import numpy as np
import datetime
import ogr, osr
import pandas
import pytz
import ODM
from django.db import connection
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

################################################################################################
################################################################################################
################################################################################################
################################################################################################


## Note that:
## datetime.strptime is a function used to convert  string to datetime type
## .strftime is a method used to convert datetime type to string

dbname = "DEI3"
user = "postgres"
host = "localhost"
port = "5432"
password ="maithang1990"


# Get dir path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def upload(request):
    return render_to_response('uploadfile.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_methods(request):
    return render_to_response('upload_methods.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_sources(request):
    return render_to_response('upload_sources.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_variables(request):
    return render_to_response('upload_variables.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_sites(request):
    return render_to_response('upload_sites.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def upload_datavalues(request):
    return render_to_response('upload_datavalues.html',context_instance=RequestContext(request))


@csrf_exempt
@login_required(login_url="/auth/require_login")
def confirm_upload(request):
    USER_NAME = request.user.username
    fileName = str((request.FILES['upload_file']).name)
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files/')+fileName
    print type(request.FILES['upload_file'])
    print pandas.read_csv(request.FILES['upload_file'])

    if os.path.exists(FILE_DIR):
        os.remove(FILE_DIR)

    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            args = {}
            args.update(csrf(request))
            if 'datavalue' in fileName :
                importType = 'datavalues'
            elif 'site' in fileName:
                importType = 'sites'
            elif 'method' in fileName:
                importType = 'methods'
            elif 'source' in fileName:
                importType = 'sources'
            elif 'variable' in fileName:
                importType = 'variables'
            args['fileName'] = fileName
            return render_to_response('import_'+importType+'.html',args)
    else:
        form = UploadForm()
    args = {}
    args['filename'] = filename
    args.update(csrf(request))
    args['form'] = form

    return render_to_response('uploadfile.html',args,context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def save_methods(request):
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    dbConnection = connection
    try:
        methodObj = ODM.Methods(FILE_DIR+'/methods.csv',dbConnection)
        methodObj.importData()
        return render_to_response('successfull_import.html',context_instance=RequestContext(request))
    except:
        dbConnection.close()
        return render_to_response('error_import.html',context_instance=RequestContext(request))



@login_required(login_url="/auth/require_login")
def save_sources(request):
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    dbConnection = connection
    try:
        sourcesObj = ODM.Sources(FILE_DIR+'/sources.csv',dbConnection)
        sourcesObj.importData()
        return render_to_response('successfull_import.html',context_instance=RequestContext(request))
    except:
        dbConnection.close()
        return render_to_response('error_import.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def save_variables(request):
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    dbConnection = connection
    try:
        variablesObj = ODM.Variables(FILE_DIR+'/variables.csv',dbConnection)
        variablesObj.importData()
        dbConnection.close()
        return render_to_response('successfull_import.html',context_instance=RequestContext(request))
    except:
        dbConnection.close()
        return render_to_response('error_import.html',context_instance=RequestContext(request))


@login_required(login_url="/auth/require_login")
def save_sites(request):
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    dbConnection = connection
    try:
        siteOject = ODM.Sites(FILE_DIR+'/sites.csv',dbConnection)
        siteOject.importData()
        del siteOject
        dbConnection.close()
        return render_to_response('successfull_import.html',context_instance=RequestContext(request))
    except:
        dbConnection.close()
        return render_to_response('error_import.html',context_instance=RequestContext(request))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def save_datavalues(request):
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    print type(request.FILES['upload_file'])
    importData = request.FILES['upload_file']
    dbConnection = connection
    datetimeFormat = str(request.POST['datetimeFormat'])
    dataTimeZone =  str(request.POST['timezone'])
    public = str(request.POST['public'])

    if public.lower() == 'yes':
        public = 'TRUE'
    else:
        public = 'FALSE'

    if request.user.is_staff:
        uploadUser = 'admin'
    else:
        uploadUser = USER_NAME

    try:
        dataValuesObj = ODM.DataValues(importData,
                                       dbConnection,datetimeFormat=datetimeFormat,
                                       dataTimeZone=dataTimeZone,
                                       uploadUser=uploadUser,
                                       public=public)
    except Exception as e:
        args = {}
        args['error'] =  e.message
        dbConnection.close()
        return render_to_response('error_import.html',args,context_instance=RequestContext(request))

    try:
        dataValuesObj.importData()
        dbConnection.close()
        return render_to_response('successfull_import.html',context_instance=RequestContext(request))
    except Exception as e:
        args = {}
        args['error'] =  e.message
        dbConnection.close()
        return render_to_response('error_import.html',args,context_instance=RequestContext(request))


@csrf_exempt
@login_required(login_url="/auth/require_login")
def download_sample(request,name):
    url = '/protected/importfile_sample/'+ name
    response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(name)
    response['X-Accel-Redirect'] = url
    return response

@csrf_exempt
@login_required(login_url="/auth/require_login")
def deleteData(request):
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
    selected_sitename = request.POST.getlist('selected_sitename[]',[0,0,0,0])

    dbConnection = ODM.createDBConection(dbname=dbname, user=user, password=password, host=host, port=port)


    return HttpResponse("You succcessfully edited %s rows in database"%(len(selected_id)))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def delete_sites(request):
    selected_id = request.POST.getlist('id[]',[0,0,0,0])
    selected_name = request.POST.getlist('name[]',[0,0,0,0])

    dbConnection = ODM.createDBConection(dbname=dbname, user=user, password=password, host=host, port=port)
    ODM.delAllSitesData(dbConnection,list(selected_id))

    return HttpResponseRedirect('/gis/update_geojson')


@csrf_exempt
@login_required(login_url="/auth/require_login")
def updateEditedData(request):
    selectedID = request.POST.get('id')
    selectedVariable = request.POST.get('variable')
    datetime = request.POST.getlist('datetime[]',[0,0,0,0])
    editedValue = request.POST.getlist('editedValue[]',[0,0,0,0])


    connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
    connection.commit()

    ## Create variable libary
    variable_dictonary = {}
    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID","DataType","VariableUnitsID","VariableCode" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()

    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})

    selectedVariableID = variable_dictonary[selectedVariable]
    ## Update data

    updateCursor = connection.cursor()
    n = 0

    for i in range(len(datetime)):
        if (editedValue[i]).lower() == "none" or editedValue[i] == "":
            pass
        else:
            executing_str = 'UPDATE dbo."DataValues" SET "DataValue" = %s WHERE "SiteID" = %s AND "VariableID" = %s AND "LocalDateTime" = %s'%(editedValue[i],selectedID,selectedVariableID,"'%s'"%(datetime[i]))
            updateCursor.execute(executing_str)
            connection.commit()
            n = n + 1

    return HttpResponse("You succcessfully edited %s rows in database"%(n))
