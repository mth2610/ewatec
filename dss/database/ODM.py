#!/usr/bin/python
# -*- coding: utf8 -*-
import psycopg2
import csv
import numpy as np
import datetime
import ogr, osr
import pandas
import pytz

def newRstrip(data):
    try:
        return data.rstrip()
    except:
        return data

def createDBConection(dbname,user,password,host,port):
    dbConnection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    dbConnection.commit()
    return dbConnection

def createLookupTable(dbCursor,table,key,values):
    if type(values)==list:
        columns = [key]+values
    else:
        columns = [key]+[values]
    executeStr = 'SELECT '+ ','.join(['"'+e+'"' for e in columns]) + ' FROM %s'%(table)
    dbCursor.execute(executeStr)
    data = dbCursor.fetchall()
    library = {}
    if type(values)!=list:
        for e in data:
            library.update({(newRstrip(e[0])):newRstrip(e[1])})
    else:
        numValues = len(values)
        for e in data:
            library.update({(newRstrip(e[0])):dict(zip(values,[newRstrip(value) for value in e[1:]]))})

    return library

def insertTemplate(table,columns, returning = None):
    numCols = len(columns)
    columns = ','.join(['"'+e+'"' for e in columns])
    values = 'VALUES (' + ','.join(['%s' for i in range(numCols)]) + ') '
    if returning == None:
        template = 'INSERT INTO ' + table + ' (' + columns + ') ' + values
    else:
        template = 'INSERT INTO ' + table + ' (' + columns + ') ' + values + ' RETURNING "%s"'%(returning)
    return template

def updateTemplate(table,setCols,whereCols):
    numSetCols = len(setCols)
    numWhereCols = len(whereCols)
    setValues = ' AND '.join([ '"'+e+'"' +'=%s'for e in setCols])
    whereValues = ' AND '.join([ '"'+e+'"' +'=%s'for e in whereCols])
    template = 'UPDATE %s SET '%(table) + setValues + ' WHERE ' + whereValues
    return template

def delTemplate(table,whereCols):
    'DELETE FROM dbo."SeriesCatalog" WHERE'
    numWhereCols = len(whereCols)
    whereValues = ' AND '.join([ '"'+e+'"' +'=%s'for e in whereCols])
    template = 'DELETE FROM  %s '%(table) + ' WHERE ' + whereValues
    return template

def selectMinMaxNumTemplate(table,col,whereCols):
    numWhereCols = len(whereCols)
    whereValues = ' AND '.join([ '"'+e+'"' +'=%s'for e in whereCols])
    template = 'SELECT MIN("%s"), MAX("%s"), COUNT("%s")'%(col,col,col) + 'FROM %s '%(table) + ' WHERE ' + whereValues
    return template

def selectTemplate(table,extractCols,conditionCols,sortCol,dateTimeField=''):
    extractColsStr = ', '.join(['"'+e+'"' for e in extractCols])
    conditionValues = ' AND '.join([ '"'+e+'"' +'=%s'for e in conditionCols])

    if dateTimeField == False:
        template = 'SELECT %s '+\
                   'FROM %s '+\
                   'WHERE %s '+\
                   'ORDER BY "%s"'%(extractColsStr,table,conditionValues,sortCol)
    else:
        conditionValues = conditionValues + ' AND ' + '"'+ dateTimeField +'"' +' >= %s AND '+ '"'+dateTimeField+'"' + '<= %s'
        template = 'SELECT %s FROM %s WHERE %s ORDER BY "%s"'%(extractColsStr,table,conditionValues,sortCol)

    return template

def minMaxNumOfCol(dbCursor,table,col,whereCols,whereColsValues):
    exeTemplate = selectMinMaxNumTemplate(table,col,whereCols)
    dbCursor.execute(exeTemplate,whereColsValues)
    minMaxNumData = dbCursor.fetchall()
    return (minMaxNumData[0][0],minMaxNumData[0][1],minMaxNumData[0][2])

def pointCoordinateTransformation(inputPoint,inputEPSG,outputEPSG):
    """
        convert Coordination of a point
        input point type is tuple
    """
    # create a geometry from coordinates
    outputPoint = ogr.Geometry(ogr.wkbPoint)
    outputPoint.AddPoint(float(inputPoint[0]),float(inputPoint[1]))

    # create coordinate transformation
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # transform point
    outputPoint.Transform(coordTransform)
    return (outputPoint.GetX(),outputPoint.GetY())

def pgPointGeometryFormat(point,crs=3857):
    geometry = "ST_GeomFromText('MULTIPOINT(%s %s)',%s)"%(str(point[0]),str(point[1]),crs)
    return geometry

def delData(dbCursor,table,df):
    numRows = (df.shape)[0]
    conColumns = list(df.columns.values)
    deTemplate = delTemplate(table,conColumns)

    for i in range(numRows):
        rowData = tuple(df.iloc[i])
        dbCursor.execute(deTemplate,rowData)
    return numRows

def delAllSitesData(dbConnection,sites):
    delDataValuesTemp = delTemplate('dbo."DataValues"',['SiteID'])
    delGisStationTemp = delTemplate('gis_apps_stations',['id'])
    delSitesnTemp = delTemplate('dbo."Sites"',['SiteID'])
    delSeriesCatalogTemp = delTemplate('dbo."SeriesCatalog"',['SiteID'])
    dbCursor = dbConnection.cursor()
    numSites = len(sites)

    for site in sites:
        try:
            dbCursor.execute(delDataValuesTemp,(site,))
            dbCursor.execute(delGisStationTemp,(site,))
            dbCursor.execute(delSitesnTemp,(site,))
            dbCursor.execute(delSeriesCatalogTemp,(site,))
        except Exception as isnt:
            print type(isnt)
            print isnt.args
    dbConnection.commit()

def updateSeriesCatalog(dbConnection,df):
    dbCursor = dbConnection.cursor()
    numRows = (df.shape)[0]
    conColumns = ['UTCOffset', 'SiteID', 'VariableID',
                  'CensorCode', 'SourceID', 'QualityControlLevelID',
                  'MethodID', 'UploadUser', 'Public']

    updateColumns = ["BeginDateTime","EndDateTime","BeginDateTimeUTC",
                    "EndDateTimeUTC","ValueCount"]

    insertColumns = ["SiteID","SiteCode","SiteName",
                     "SiteType","VariableID","VariableCode",
                     "VariableName","Speciation","VariableUnitsID",
                     "VariableUnitsName","SampleMedium","ValueType",
                     "TimeSupport","TimeUnitsID","TimeUnitsName",
                     "DataType","GeneralCategory","MethodID",
                     "MethodDescription","SourceID","Organization",
                     "SourceDescription","Citation","QualityControlLevelID",
                     "QualityControlLevelCode","BeginDateTime","EndDateTime",
                     "BeginDateTimeUTC","EndDateTimeUTC","ValueCount",
                     "UploadUser","Public"]


    whereConsCols = list(df.columns.values)
    whereConsCols.remove('UTCOffset')
    whereConsCols.remove('CensorCode')
    upTemplate = updateTemplate('dbo."SeriesCatalog"',
                                updateColumns,
                                whereConsCols)


    inTemplate = insertTemplate('dbo."SeriesCatalog"',insertColumns)

    ## get lookup table
    # Create SiteCode, SiteID, SiteName, SiteType libary
    siteLib = createLookupTable(dbCursor,'dbo."Sites"','SiteCode',['SiteID','SiteName','SiteType'])

    # Create VariableCode, VariableID libary
    variableLib = createLookupTable(dbCursor,'dbo."Variables"','VariableCode',
                                                      ["VariableID","VariableName","Speciation",
                                                       "VariableUnitsID","SampleMedium","ValueType",
                                                       "TimeSupport","TimeUnitsID","DataType",
                                                       "GeneralCategory"])

    # Create MethodDesciption, MethodID libary
    methodLib = createLookupTable(dbCursor,'dbo."Methods"','MethodDescription','MethodID')

    # Create UnitID, UnitName libary
    unitLib = createLookupTable(dbCursor,'dbo."Units"','UnitsID','UnitsName')

    # Create SourceID, Organization, SourceDescription, Citation libary
    sourceLib = createLookupTable(dbCursor,'dbo."Sources"','SourceID',['Organization','SourceDescription','Citation'])

    # Create QualityControlLevelID, QualityControlLevelCode libary
    qualityControlLevelLib = createLookupTable(dbCursor,'dbo."QualityControlLevels"','QualityControlLevelID','QualityControlLevelCode')
    for i in range(numRows):
        ## Get data of a row and convert to list
        rowData = df.iloc[i]
        ## Get min max from LocalDatetime of 'dbo.DataValues'
        minDatetime, maxDateTime, numData = minMaxNumOfCol(dbCursor,'dbo."DataValues"','LocalDateTime',conColumns,
                                                           [rowData['UTCOffset'],
                                                           siteLib[rowData['SiteCode']]['SiteID'],
                                                           variableLib[rowData['VariableCode']]['VariableID'],
                                                           rowData['CensorCode'],
                                                           rowData['SourceID'],
                                                           rowData['QualityControlLevelID'],
                                                           methodLib[rowData['MethodDescription']],
                                                           rowData['UploadUser'],
                                                           rowData['Public']])
        minUTCDatetime, maxUTCDateTime, numData = minMaxNumOfCol(dbCursor,'dbo."DataValues"','DateTimeUTC',conColumns,
                                                           [rowData['UTCOffset'],
                                                           siteLib[rowData['SiteCode']]['SiteID'],
                                                           variableLib[rowData['VariableCode']]['VariableID'],
                                                           rowData['CensorCode'],
                                                           rowData['SourceID'],
                                                           rowData['QualityControlLevelID'],
                                                           methodLib[rowData['MethodDescription']],
                                                           rowData['UploadUser'],
                                                           rowData['Public']])
        try:
            ## Update
            tupledata = (minDatetime,maxDateTime,minUTCDatetime,
                         maxUTCDateTime,numData,rowData["SiteCode"],
                         rowData["VariableCode"],rowData["SourceID"],
                         rowData["QualityControlLevelID"],rowData["MethodDescription"],rowData["UploadUser"],
                         rowData["Public"])
            dbCursor.execute(upTemplate,tupledata)
        except Exception as inst:
            ## Insert
            dbCursor.execute(inTemplate,(siteLib[rowData["SiteCode"]]["SiteID"],
                                         rowData["SiteCode"],
                                         siteLib[rowData["SiteCode"]]["SiteName"],
                                         siteLib[rowData["SiteCode"]]["SiteType"],
                                         variableLib[rowData["VariableCode"]]["VariableID"],
                                         rowData["VariableCode"],
                                         variableLib[rowData["VariableCode"]]["VariableName"],
                                         variableLib[rowData["VariableCode"]]["Speciation"],
                                         variableLib[rowData["VariableCode"]]["VariableUnitsID"],
                                         unitLib[variableLib[rowData["VariableCode"]]["VariableUnitsID"]],
                                         variableLib[rowData["VariableCode"]]["SampleMedium"],
                                         variableLib[rowData["VariableCode"]]["ValueType"],
                                         variableLib[rowData["VariableCode"]]["TimeSupport"],
                                         variableLib[rowData["VariableCode"]]["TimeUnitsID"],
                                         unitLib[variableLib[rowData["VariableCode"]]["TimeUnitsID"]],
                                         variableLib[rowData["VariableCode"]]["DataType"],
                                         variableLib[rowData["VariableCode"]]["GeneralCategory"],
                                         methodLib[rowData["MethodDescription"]],
                                         rowData["MethodDescription"],
                                         rowData["SourceID"],
                                         sourceLib[rowData["SourceID"]]["Organization"],
                                         sourceLib[rowData["SourceID"]]["SourceDescription"],
                                         sourceLib[rowData["SourceID"]]["Citation"],
                                         rowData["QualityControlLevelID"],
                                         qualityControlLevelLib[rowData["QualityControlLevelID"]],
                                         minDatetime,
                                         maxDateTime,
                                         minUTCDatetime,
                                         maxUTCDateTime,
                                         numData,
                                         rowData["UploadUser"],
                                         rowData["Public"]))
        except Exception as inst:
            break

        ## commit and close
        dbConnection.commit()

def getDataValue(dbConnection,siteID,variableID,
                 minDateTime,maxDateTime,requestUser='admin',
                 timeZone='LocalDateTime',dateTimeFormat="%m/%d/%Y %H:%M:%S"):
    """
        This is a function to extract data from dbo."DataValues"
        The input of the funtion is a pandas DataFrame
        including condition of queries and It must contain
        "SiteID","VariableID","minLocalDatetime","maxLocalDateTime"
    """
    dbCursor = dbConnection.cursor()
    table = 'dbo."DataValues"'
    extractCols = ["LocalDateTime","DataValue"]
    sortCol = "LocalDateTime"

    if type(minDateTime) == str and type(maxDateTime)== str:
        minDateTime = datetime.datetime.strptime(minDateTime,dateTimeFormat)
        maxDateTime = datetime.datetime.strptime(maxDateTime,dateTimeFormat)

    if requestUser == 'admin':
        conditionCols = ["SiteID","VariableID"]
        selectTemp = selectTemplate(table,extractCols,conditionCols,sortCol,dateTimeField="LocalDateTime")
        dbCursor.execute(selectTemp,(siteID,variableID,minDateTime,maxDateTime))

    else:
        conditionCols = ["SiteID","VariableID","User","Public"]
        selectTemp = selectTemplate(table,extractCols,conditionCols,sortCol,dateTimeField="LocalDateTime")
        dbCursor.execute(selectTemp,(siteID,variableID,minDateTime,maxDateTime,requestUser))
    dbConnection.commit()
    data = dbCursor.fetchall()
    dbConnection.close()

    return (pandas.DataFrame(data, columns=['DateTime','Value'])).set_index(['DateTime'])

class Methods():
    def __init__(self, filePath,dbConnection):
        methodsObj = pandas.read_csv(filePath)
        methodsObj = methodsObj.where((pandas.notnull(methodsObj)), None)
        self.methodsObj = methodsObj
        self.dbConnection = dbConnection
        self.dbCursor = dbConnection.cursor()
    def importData(self):
        dbConnection = self.dbConnection
        dbCursor = self.dbCursor
        methodsObj = self.methodsObj
        numRows = (methodsObj.shape)[0]

        # data using for dbo."Methods"
        methodsCols = ["MethodDescription","MethodLink"]
        methodsTemplate = insertTemplate('dbo."Methods"',methodsCols)
        for i in range(numRows):
            dbCursor.execute(methodsTemplate,
                             (methodsObj["MethodDescription"][i],
                              methodsObj["MethodLink"][i]))
        dbConnection.commit()
        return numRows

class Sources():
    def __init__(self, filePath,dbConnection):
        sourcesObj = pandas.read_csv(filePath)
        sourcesObj = sourcesObj.where((pandas.notnull(sourcesObj)), None)
        self.sourcesObj = sourcesObj
        self.dbConnection = dbConnection
        self.dbCursor = dbConnection.cursor()
    def importData(self):
        dbConnection = self.dbConnection
        dbCursor = self.dbCursor
        sourcesObj = self.sourcesObj
        numRows = (sourcesObj.shape)[0]
        # data using for dbo."Source"
        sourcesCols = ["Organization","SourceDescription","SourceLink",
                       "ContactName","Phone","Email",
                       "Address","City","State",
                       "ZipCode","Citation","MetadataID"]
        sourceTemplate = insertTemplate('dbo."Sources"',sourcesCols)
        for i in range(numRows):
            dbCursor.execute(sourceTemplate,
                             (sourcesObj["Organization"][i],
                             sourcesObj["SourceDescription"][i],
                             sourcesObj["SourceLink"][i],
                             sourcesObj["ContactName"][i],
                             sourcesObj["Phone"][i],
                             sourcesObj["Email"][i],
                             sourcesObj["Address"][i],
                             sourcesObj["City"][i],
                             sourcesObj["SourceState"][i],
                             sourcesObj["Address"][i],
                             sourcesObj["Citation"][i],
                             sourcesObj["MetadataID"][i]))

        dbConnection.commit()
        return numRows

class Variables():
    def __init__(self, filePath,dbConnection):
        variablesObj = pandas.read_csv(filePath)
        variablesObj = variablesObj.where((pandas.notnull(variablesObj)), None)
        self.variablesObj = variablesObj
        self.dbConnection = dbConnection
        self.dbCursor = dbConnection.cursor()
    def importData(self):
        dbConnection = self.dbConnection
        dbCursor = self.dbCursor
        variablesObj = self.variablesObj
        numRows = (variablesObj.shape)[0]

        ## Data using for dbo."Variables"
        variablesCols = ["VariableCode","VariableName","Speciation",
                         "VariableUnitsID","SampleMedium","ValueType",
                         "IsRegular","TimeSupport","TimeUnitsID",
                         "DataType","GeneralCategory","NoDataValue"]
        variablesTemplate = insertTemplate('dbo."Variables"',variablesCols)
        # Create VariableUnitsName - VariableUnitsID lib
        variableUnitsName_variableUnitsID_lib = createLookupTable(dbCursor,'dbo."Units"','UnitsName','UnitsID')
        for i in range(numRows):
            dbCursor.execute(variablesTemplate,
                             (variablesObj["VariableCode"][i],
                              variablesObj["VariableName"][i],
                              variablesObj["Speciation"][i],
                              variableUnitsName_variableUnitsID_lib[variablesObj['VariableUnitsName'][i]],
                              variablesObj["SampleMedium"][i],
                              variablesObj["ValueType"][i],
                              str(variablesObj["IsRegular"][i]),
                              variablesObj["TimeSupport"][i],
                              variableUnitsName_variableUnitsID_lib[variablesObj["TimeUnitsName"][i]],
                              variablesObj["DataType"][i],
                              variablesObj["GeneralCategory"][i],
                              variablesObj["NoDataValue"][i]))
        dbConnection.commit()
        return numRows

class Sites():
    def __init__(self, filePath,dbConnection, datetimeFormat="%m/%d/%Y %H:%M:%S"):
        sitesObj = pandas.read_csv(filePath)
        sitesObj = sitesObj.where((pandas.notnull(sitesObj)), None)
        self.sitesObj = sitesObj
        self.dbConnection = dbConnection
        self.dbCursor = dbConnection.cursor()
    def importData(self):
        dbConnection = self.dbConnection
        dbCursor = self.dbCursor
        siteObj = self.sitesObj
        numRows = (siteObj.shape)[0]

        ## data using for dbo."Sites"
        columnList1 = ["SiteCode","SiteName","Latitude",\
                      "Longitude","LatLongDatumID","Elevation_m",\
                      "VerticalDatum","LocalX","LocalY",\
                      "LocalProjectionID","PosAccuracy_m","State",\
                      "County","Comments"]
        executeTemplate1 = insertTemplate('dbo."Sites"',columnList1,returning = "SiteID")
        projectionID_projectionName_lib = createLookupTable(dbCursor,'dbo."SpatialReferences"','SRSName','SpatialReferenceID')

        ## dara using for gis_app_stations
        columnList2 = ["id","name","sitecode","geometry"]
        executeTemplate2 = insertTemplate('gis_apps_stations',columnList2)


        for i in range(numRows):
            ## insert data to dbo."Sites"
            dbCursor.execute(executeTemplate1,(siteObj["SiteCode"][i],
                                              siteObj["SiteName"][i],
                                              siteObj["Latitude"][i],
                                              siteObj["Longitude"][i],
                                              projectionID_projectionName_lib[siteObj["LatLongDatumSRSName"][i]],
                                              siteObj["Elevation_m"][i],
                                              siteObj["VerticalDatum"][i],
                                              siteObj["LocalX"][i],
                                              siteObj["LocalY"][i],
                                              projectionID_projectionName_lib[siteObj["LocalProjectionSRSName"][i]],
                                              siteObj["PosAccuracy_m"][i],
                                              siteObj["State"][i],
                                              siteObj["County"][i],
                                              siteObj["Comments"][i]))
            ## get SiteID
            siteID = dbCursor.fetchone()[0]
            geometry = pgPointGeometryFormat(pointCoordinateTransformation((siteObj["Longitude"][i],
                                                                            siteObj["Latitude"][i]),
                                                                            4326,
                                                                            3857))
            ## insert data to dbo."Sites"
            dbCursor.execute(executeTemplate2%(siteID,
                                               "'"+siteObj["SiteName"][i]+"'",
                                               "'"+siteObj["SiteCode"][i]+"'",
                                               geometry))
        ## commit and close
        dbConnection.commit()

class DataValues():
    def __init__(self, filePath,dbConnection, datetimeFormat="%m/%d/%Y %H:%M:%S", dataTimeZone ='Asia/Ho_Chi_Minh',uploadUser='admin',public='TRUE'):
        dataValuesObj = pandas.read_csv(filePath)
        dataValuesObj.loc[(dataValuesObj["QualityControlLevelID"]).isnull(),"QualityControlLevelID"] = int(-9999)
        dataValuesObj.loc[(dataValuesObj["CensorCode"]).isnull(),"CensorCode"] = 'nc'
        dataValuesObj = dataValuesObj.where((pandas.notnull(dataValuesObj)), None)
        dataValuesObj['LocalDateTime'] = pandas.to_datetime(dataValuesObj['LocalDateTime'], format=datetimeFormat)
        self.dataValuesObj = dataValuesObj
        self.dataTimeZone = pytz.timezone('Asia/Ho_Chi_Minh')
        self.dbConnection = dbConnection
        self.dbCursor = dbConnection.cursor()

        ## Add UploadUser and Puclic column
        dataValuesObj['UploadUser'] = uploadUser
        dataValuesObj['Public'] = public

    def importData(self):
        dbConnection = self.dbConnection
        dbCursor = self.dbCursor
        datavaluesObj = self.dataValuesObj
        numRows = (datavaluesObj.shape)[0]
        dataTimeZone = self.dataTimeZone

        ## data using for dbo."DataValues"
        dataValuesCols = ["DataValue","LocalDateTime","UTCOffset",\
                          "DateTimeUTC","SiteID","VariableID",\
                          "CensorCode","MethodID","SourceID",\
                          "QualityControlLevelID","UploadUser","Public"]
        datValuesInsertTemplate = insertTemplate('dbo."DataValues"',dataValuesCols)
        datValuesUpdateTemplate = updateTemplate('dbo."DataValues"',["DataValue"],
                                                 ["LocalDateTime","UTCOffset","DateTimeUTC",\
                                                  "SiteID","VariableID","CensorCode",\
                                                  "MethodID","SourceID","QualityControlLevelID",
                                                  "UploadUser","Public"])
        ##
        UTC_OFFSET_TIMEDELTA = (dataTimeZone.utcoffset(datetime.datetime.now()))
        UTC_OFFSET = UTC_OFFSET_TIMEDELTA.seconds/(60*60)
        ## get lookup table
        # Create SiteCode, SiteID libary
        siteCode_siteID_lib = createLookupTable(dbCursor,'dbo."Sites"','SiteCode','SiteID')

        # Create VariableCode, VariableID libary
        variableCode_variableID_=_lib = createLookupTable(dbCursor,'dbo."Variables"','VariableCode','VariableID')

        #Create MethodID, MethodDesciption
        methodDesciption_methodID_lib = createLookupTable(dbCursor,'dbo."Methods"','MethodDescription','MethodID')

        ## Insert data into dbo."DataValues"
        for i in range(numRows):
            try:
                dbCursor.execute(datValuesInsertTemplate,(datavaluesObj["DataValue"][i],
                                                          datavaluesObj["LocalDateTime"][i],
                                                          UTC_OFFSET,
                                                          datavaluesObj["LocalDateTime"][i] - UTC_OFFSET_TIMEDELTA,
                                                          siteCode_siteID_lib[datavaluesObj["SiteCode"][i]],
                                                          variableCode_variableID_[datavaluesObj["VariableCode"][i]],
                                                          datavaluesObj["CensorCode"][i],
                                                          methodDesciption_methodID_lib[datavaluesObj["MethodDescription"][i]],
                                                          datavaluesObj["SourceID"][i],
                                                          datavaluesObj["QualityControlLevelID"][i],
                                                          datavaluesObj["UploadUser"][i],
                                                          datavaluesObj["Public"][i]))

            except Exception as inst:
                dbConnection.rollback()
                if datavaluesObj["DataValue"][i] != -9999:
                    dbCursor.execute(datValuesUpdateTemplate,(datavaluesObj["DataValue"][i],
                                                              datavaluesObj["LocalDateTime"][i],
                                                              UTC_OFFSET,
                                                              datavaluesObj["LocalDateTime"][i] - UTC_OFFSET_TIMEDELTA,
                                                              siteCode_siteID_lib[datavaluesObj["SiteCode"][i]],
                                                              variableCode_variableID_[datavaluesObj["VariableCode"][i]],
                                                              datavaluesObj["CensorCode"][i],
                                                              methodDesciption_methodID_lib[datavaluesObj["MethodDescription"][i]],
                                                              datavaluesObj["SourceID"][i],
                                                              datavaluesObj["QualityControlLevelID"][i],
                                                              datavaluesObj["UploadUser"][i],
                                                              datavaluesObj["Public"][i]
                                                              ))
            except Exception as inst:
                break

        ## Update serialCatalog
        groupDataValueObj = (datavaluesObj.groupby(['UTCOffset','SiteCode','VariableCode',
                                      'CensorCode','SourceID','QualityControlLevelID',
                                      'MethodDescription','UploadUser','Public'])).mean().reset_index()
        groupDataValueObj = groupDataValueObj.drop('DataValue',1)
        dbConnection.commit()
        updateSeriesCatalog(dbConnection,groupDataValueObj)
