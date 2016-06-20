from django.shortcuts import render
from rest_framework import viewsets
from . import serializers
from gis_apps.models import stations as Stations
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework import filters
from database import ODM
from django.db import connection

# Create your views here.

class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows sites to be viewed or edited.
    """
    queryset = Stations.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('name', 'sitecode')
    serializer_class = serializers.SiteSerializer

class DataValueView(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user.username
        parameter = request.GET
        siteID = int(parameter['siteid'])
        variableID = int(parameter['variableid'])
        minDateTime = parameter['mindatetime']
        maxDateTime = parameter['maxdatetime']
        data = ODM.getDataValue(connection,siteID,variableID,
                            minDateTime,maxDateTime,requestUser='admin',timeZone='LocalDateTime')
        response = Response(data.to_json(orient='records'))
        return response
