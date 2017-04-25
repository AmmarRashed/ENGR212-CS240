from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from .models import Tag
from .forms import TagForm

def show_tag(request):

    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            return HttpResponse("Not Valid")

    elif request.method == "GET":
        form = TagForm()

    return render(request, "my_tags.html", {"tags": Tag.objects.all(),
                                            "form": form})
