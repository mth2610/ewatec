import os.path
from models import landuse
from django.contrib.gis.utils import LayerMapping


filename = str(raw_input('Enter name of shape file: '))
code_field = str(raw_input('Enter name of code field: '))
desciption_field = str(raw_input('Enter name of desciption field: '))


if desciption_field == None or desciption_field == "":
    mapping = {
        'code' : code_field,
        'geometry' : 'MULTIPOLYGON',
    }
else:
    mapping = {
        'code' : code_field,
        'desciption' : desciption_field,
        'geometry' : 'MULTIPOLYGON',
    }

fname = os.path.abspath(os.path.join(os.path.dirname(__file__), filename+'.shp'))

def run(verbose=True):
    lm = LayerMapping(landuse, fname , mapping,
                      transform=True, encoding='UTF-8')

    lm.save(strict=True, verbose=verbose)  

