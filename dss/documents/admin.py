from django.contrib import admin

# Example how to add rich editor capabilities to your models in admin.
from django.contrib.admin import site, ModelAdmin
 
import models
 
# we define our resources to add to admin pages
class CommonMedia:
    js = (
    'https://ajax.googleapis.com/ajax/libs/dojo/1.8.1/dojo/dojo.xd.js',
    '/static/js/editor.js',
    )
    css = {
    'all': ('/static/css/editor.css',),
    }
 
# let's add it to this model
site.register(models.Article,
  list_display  = ('body',),
  search_fields = ['person',],
  Media = CommonMedia,
)
 