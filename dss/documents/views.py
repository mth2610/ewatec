from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import simplejson
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
import tempfile
import itertools
import os
import psycopg2
from gis_apps import models
import csv
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from forms import ArticleForm
from documents.models import Article
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger


# Create your views here.

def documents(request):
    return render_to_response('documents.html',context_instance=RequestContext(request))

@login_required(login_url="/auth/require_login")
def newpaper(request):
	return render_to_response('newpaper.html',context_instance=RequestContext(request))

@csrf_exempt
@login_required(login_url="/auth/require_login")
def create(request):
    if request.method == 'POST':        
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/documents/showpage/1/')
    else:
        form = ArticleForm()

    args = {}
    args.update(csrf(request))

    args['form'] = form
    
    
    return render_to_response('documents.html',args, context_instance=RequestContext(request))

@csrf_exempt
def showpaper(request,page):
    args = {}
    data_list = Article.objects.all()
    entries_per_page = 2
    paginator = Paginator(data_list, entries_per_page)
#    page = request.GET.get('page')
    print page  
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        data = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        data = paginator.page(paginator.num_pages)
        
    args["data"] = data
    return render_to_response('documents.html',args,context_instance=RequestContext(request))

def papercontent(request, article_id = 1):
    return render_to_response('papercontent.html', {'article':Article.objects.get(id = article_id)},context_instance=RequestContext(request))

    