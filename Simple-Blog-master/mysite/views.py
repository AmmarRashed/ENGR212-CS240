from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, render
from blog.models import animals

def login(request):

    return HttpResponseRedirect(r'http://127.0.0.1:8000/blog/entries')

def search(request):
    if 'q' in request.GET and request.GET['q']:
        q = request.GET['q']
        results = [animal for animal in animals.values() if q in animal]
        # message = 'You searched for: %r' %request.GET['q']
        return render_to_response('search_results.html',{'animals':results,'query':q})
    else:
        return render_to_response('search_form.html')