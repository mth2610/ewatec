from django.shortcuts import render_to_response
from django.template import RequestContext
from documents.models import Article
# Create your views here.

def index(request):
    args = {}
    
    page = []
    
    try:
        page1 = Article.objects.get(pk=1)
        page.append(page1)
    except:
        pass 

    try:
        page2 = Article.objects.get(pk=2)
        page.append(page2)
    except:
        pass 
    
    try:
        page3 = Article.objects.get(pk=3)
        page.append(page3)
    except:
        pass 
    
    try:
        page4 = Article.objects.get(pk=4)
        page.append(page1)
    except:
        pass 
    
    if page == []:
        page = None
    else:
        pass

        
    args['page'] = page

    return render_to_response('mainpage.html',args,context_instance=RequestContext(request))

def database(request):
    return render_to_response('database.html',context_instance=RequestContext(request))
