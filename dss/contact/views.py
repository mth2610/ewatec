from django.shortcuts import render
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from forms import ContactForm
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.context_processors import csrf

# Create your views here.

#@login_required(login_url="/auth/require_login")

def contact(request):
    return render_to_response('contact.html',context_instance=RequestContext(request))

@csrf_exempt
def save_contact(request):
    if request.method == 'POST':        
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, u'Your message were successfully sended.')
            return HttpResponseRedirect('/contact/view_contact')
    else:
        form = ContactForm()

    args = {}
    args.update(csrf(request))
    args['form'] = form
    
    
    return render_to_response('contact.html',args, context_instance=RequestContext(request))