from django.db import models
from time import time
import os 

# Create your models here.

def get_upload_file_dir(instance,filename):
    directory = '/'.join(['user', instance.user,'temporary_files', filename])

    if os.path.exists(directory):
        pass
    else:
        os.makedirs
        
    return directory

class Upload(models.Model):
    upload_file = models.FileField(upload_to = get_upload_file_dir)
    user = models.CharField(max_length=50)
    def __unicode__(self):
        return self.title