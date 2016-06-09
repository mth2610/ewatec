from django.db import models
from django.contrib.gis.db import models
import os 
# Create your models here.


def get_upload_file_dir(instance,filename):
    directory = '/'.join(['user', instance.user,'temporary_files', filename])
    if os.path.exists(directory):
        pass
    else:
        os.makedirs
    return directory
	
	
class province_boundary(models.Model):
    province = models.CharField(max_length=254)
    population = models.FloatField(null=True)
    area = models.FloatField(null=True)
    objects = models.GeoManager()
    geometry = models.MultiPolygonField(srid =3857)
    def __str__(self):
        return self.province

    
class stations(models.Model):
    name = models.CharField(max_length=254)
    sitecode = models.CharField(max_length=254)
    objects = models.GeoManager()
    geometry = models.MultiPointField(srid =3857)
    def __str__(self):
        return self.name
 
class landuse(models.Model):
    code = models.CharField(max_length=3)
    description = models.CharField(max_length=255,null=True)
    objects = models.GeoManager()
    geometry = models.MultiPolygonField(srid =3857)
    def __str__(self):
        return self.code

class Upload(models.Model):
    upload_file = models.FileField(upload_to = get_upload_file_dir)
    user = models.CharField(max_length=50)
    def __unicode__(self):
        return self.title
			
class user_map(models.Model):
    link = models.CharField(max_length=255)
    types = models.CharField(max_length=10,null=True)
    user = models.CharField(max_length=50)
    
    def __str__(self):
        return self.code
    