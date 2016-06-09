from rest_framework_gis import serializers
from gis_apps import models as gisapps_models

class SiteSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = gisapps_models.stations
        geo_field = "geometry"
        id_field = False
        fields = ('id', 'name', 'sitecode')
