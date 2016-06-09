from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.conf import settings as django_settings
from time import time

def get_upload_file_name(instance,filename):
    return "user_avatar/%s_%s"%(str(time()).replace('.','_'),filename)

## Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User)
    picture = models.ImageField(upload_to = get_upload_file_name)
    institution = models.CharField(max_length=50)
    def __unicode__(self):
        return self.user
    
    
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)