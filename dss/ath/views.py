
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import auth
from forms import MyRegistrationForm
#from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf
from django.template import RequestContext
from django.core.urlresolvers import reverse
from forms import ProfileForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings as django_settings
from django.contrib import messages
import os

def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.



def ip_address_processor(request):
    return {'ip_address': request.META['REMOTE_ADDR']}

@csrf_exempt
def login(request):
    c = {}
    c.update(csrf(request))    
    return render_to_response('login.html')

@csrf_exempt    
def auth_view(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    
    if user is not None:
        auth.login(request, user)
#        return HttpResponseRedirect('/auth/loggedin')
        return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/auth/invalid_login')
@csrf_exempt    
def loggedin(request):
    return render_to_response('loggedin.html', {'full_name': request.user.username},context_instance=RequestContext(request))
#    return render_to_response('loggedin.html', {'full_name': request.user.username})

@csrf_exempt
def invalid_login(request):
    return render_to_response('invalid_login.html',context_instance=RequestContext(request))

def logout(request):
    # Get dir path
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    USER_NAME = request.user.username
    FILE_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_files')
    MAP_DIR = os.path.join(BASE_DIR, 'media/user/'+USER_NAME+"/"+'temporary_maps')
    
    if os.path.exists(FILE_DIR):
        files = get_filepaths(FILE_DIR)
        for e in files:
            os.remove(e)
            
    if os.path.exists(FILE_DIR):
        files = get_filepaths(MAP_DIR)
        for e in files:
            os.remove(e)
            
    auth.logout(request)
    return render_to_response('logout.html',context_instance=RequestContext(request))

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'Your profile were successfully edited.')
            return HttpResponseRedirect('/auth/register_success')
        
    else:
        form = MyRegistrationForm()
    args = {}
    args.update(csrf(request))
    
    args['form'] = form
    
    return render_to_response('register.html', args,context_instance=RequestContext(request))


@csrf_exempt
def register_success(request):
    return render_to_response('register_success.html',context_instance=RequestContext(request))


@csrf_exempt
def require_login(request):
    return render_to_response('require_login.html',context_instance=RequestContext(request))

@csrf_exempt
def permission_error(request):
    return render_to_response('permission_error.html',context_instance=RequestContext(request))

@csrf_exempt
@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST,request.FILES,instance=request.user.profile)
        print request.FILES
        if form.is_valid():
            form.save()
            return  HttpResponseRedirect('/auth/profile')
    else:
        form = ProfileForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('profile.html', args,context_instance=RequestContext(request))

 
