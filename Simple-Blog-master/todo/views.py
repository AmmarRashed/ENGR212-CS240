from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

# Create your views here.
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render

from tags.models import Tag
from .models import Todo
from .forms import TodoForm

def show_todo(request):

    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.owner = request.user
            todo.save()
            form.save_m2m()

    elif request.method == "GET":
        form = TodoForm()

    return render(request, "my_todos.html", {"todos": Todo.objects.filter(owner=request.user.id),
                                             "tags": Tag.objects.all(),
                                             "form": form})

def get_todo(request, todo_id):
    try:
        todo = Todo.objects.get(id=todo_id)
        if request.user.id != todo.owner.id:
            raise PermissionDenied
        return render(request, "detailed_todo.html", {"todo": todo})
    except Todo.DoesNotExist:
        raise Http404("We don't have any.")

@permission_required('is_superuser')
def show_all_todo(request):
    return render(request, "my_todos.html", {"todos": Todo.objects.all()})

@permission_required('is_superuser')
def show_all_todo_from_user(request, userId):
    return render(request, "my_todos.html", {"todos": Todo.objects.filter(owner=userId)})
