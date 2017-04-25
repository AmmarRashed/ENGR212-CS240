from django.conf.urls import url

from .views import show_tag

urlpatterns = [
    url(r'^$', show_tag),
]
