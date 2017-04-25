from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^$', show_todo),
    url(r'^(?P<todo_id>[0-9]+)', get_todo),
    url(r'^all/$', show_all_todo),
    url(r'^all/user/(?P<userId>[0-9]+)$', show_all_todo_from_user),
]
