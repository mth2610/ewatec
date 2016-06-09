#!/usr/bin/python
# -*- coding: utf8 -*-
from shape import shapefile
import os
try:
    import ogr,osr
except:
    from osgeo import ogr, osr

def reprojectshp(inputfile,input_filedir,outputprj):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    # get the input layer
    inDataSet = driver.Open(input_filedir + '/' +inputfile)
    inLayer = inDataSet.GetLayer()
    inLayer_geometrytype = inLayer.GetGeomType()

    # input SpatialReference
    inSpatialRef = inLayer.GetSpatialRef()


    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputprj)

    # create the CoordinateTransformation
    coordTrans = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # create the output layer
    outputShapefile = input_filedir + '/' + inputfile.replace('.shp','')+'_3857.shp'
    if os.path.exists(outputShapefile):
        driver.DeleteDataSource(outputShapefile)
    outDataSet = driver.CreateDataSource(outputShapefile)
    outLayer = outDataSet.CreateLayer((inputfile.replace('.shp','')).encode('utf-8'), geom_type=inLayer_geometrytype)

    # add fields
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    # get the output layer's feature definition
    outLayerDefn = outLayer.GetLayerDefn()

    # loop through the input features
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        # get the input geometry
        geom = inFeature.GetGeometryRef()
        # reproject the geometry
        geom.Transform(coordTrans)
        # create a new feature
        outFeature = ogr.Feature(outLayerDefn)
        # set the geometry and attribute
        outFeature.SetGeometry(geom)
        for i in range(0, outLayerDefn.GetFieldCount()):
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
        # add the feature to the shapefile
        outLayer.CreateFeature(outFeature)
        # destroy the features and get the next input feature
        outFeature.Destroy()
        inFeature.Destroy()
        inFeature = inLayer.GetNextFeature()

    # close the shapefiles
    inDataSet.Destroy()
    outDataSet.Destroy()
    return  inputfile.replace('.shp','')+'_3857.shp',input_filedir
    
def shp2geojs(inputname,inputpath,outputpath):
    # read the shapefile
    reader = shapefile.Reader((inputpath+"/"+inputname).encode('utf-8'))
    fields = reader.fields[1:]
    field_names = [(field[0]).encode('utf-8') for field in fields]
    field_names = [(field[0])for field in fields]
    buffer = []
    a = reader.shapeRecords()
    for sr in reader.shapeRecords():
        atr = dict(zip(field_names, sr.record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", \
        geometry=geom, properties=atr)) 

#     write the GeoJSON file
    from json import dumps
    geojson = open(outputpath+"/"+(inputname.replace(".shp",".js")).replace("_3857",""), "w")
    geojson.write(dumps({"type": "FeatureCollection",\
    "features": buffer}, indent=2) + "\n")
    geojson.close()
    
    return outputpath+"/"+(inputname.replace(".shp",".js")).replace("_3857","")
    
    
