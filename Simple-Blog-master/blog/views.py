from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
# Create your views here.
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, redirect
from blog.models import *
from django.core.exceptions import PermissionDenied
from .forms import AnimalForm

def show_animals(request):
    return render(request,"animals.html",{'animals':animals_, 'length':len(animals_)})


def show_blog(request):
    '''
    # filtered_animals = animals.filter(user=request.user)
    if request.method == "POST":
        if request.user.username:
            animal = Animal.objects.create(name=request.POST.get("animal_name"),
                                description=request.POST.get("description"),
                                owner=request.user)
            animal.tags.add(*request.POST.getlist("tag_names"))
        else:
            redirect("http://127.0.0.1:8000/users/login/")
    # if not request.user.username:
    return render(request, "home.html", {"animals": Animal.objects.filter(owner=request.user.id),
                                             "tags":Tag.objects.all()})
                                             '''
    if request.method == "POST":
        form = AnimalForm(request.POST)
        if form.is_valid():
            animal = form.save(commit=False)
            animal.owner = request.user
            animal.save()
            form.save_m2m()

    elif request.method == "GET":
        form = AnimalForm()
    return render(request, "home.html", {"animals": Animal.objects.filter(owner=request.user.id),
                                         "tags": Tag.objects.all(),
                                         "form": form})

def get_animal(request,animal_id):
    try:
        animal = Animal.objects.get(id=animal_id)
        if request.user.id != animal.owner.id:
            raise PermissionDenied
        return render(request, "show_entry.html", {'animal':animal})
    except Animal.DoesNotExist:
        raise Http404("That animal does not exist in our database")


def choose_website(request):
    return render(request, "choose_website.html")

@permission_required('is_superuser')
def show_all_animals(request):
    return render(request, "home.html", {"animals": Animal.objects.all()})

@permission_required('is_superuser')
def show_all_animal_from_user(request, userId):
    return render(request, "home.html", {"animals": Animal.objects.filter(owner=userId)})
