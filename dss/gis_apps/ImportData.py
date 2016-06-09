import psycopg2
import os.path
from osgeo import ogr
from models import province_boundary
from django.contrib.gis.utils import LayerMapping


filename = str(raw_input('Enter name of shape file: '))
db = str(raw_input('Enter database name: '))
password = str(raw_input('Enter password: '))
province_field = str(raw_input('Enter name of province field: '))
population_field = str(raw_input('Enter name of population field: '))


if population_field == None or population_field == "":
    mapping = {
        'province' : province_field,
        'geometry' : 'MULTIPOLYGON',
    }
else:
    mapping = {
        'province' : province_field,
        'population' : population_field,
        'geometry' : 'MULTIPOLYGON',
    }

fname = os.path.abspath(os.path.join(os.path.dirname(__file__), filename+'.shp'))

def run(verbose=True):
    lm = LayerMapping(province_boundary, fname , mapping,
                      transform=False, encoding='UTF-8')

    lm.save(strict=True, verbose=verbose)  

