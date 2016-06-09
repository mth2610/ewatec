from django.db import models
from time import time

# Create your models here.

def get_upload_file_name(instance,filename):
    return "uploaded_file/%s_%s"%(str(time()).replace('.','_'),filename)


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    person = models.TextField()
    picture = models.ImageField(upload_to = get_upload_file_name)

    def __unicode__(self):
        return self.body




# class Comment(models.Model):
#     name = models.CharField(max_length=200)
#     body = models.TextField()
#     pub_date = models.DateTimeField('date published')
#     article = models.ForeignKey(Article)



