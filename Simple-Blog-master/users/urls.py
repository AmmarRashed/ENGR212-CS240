from django.conf.urls import url, include

from .views import signup

urlpatterns = [
    url(r'^register/$', signup),
    url(r'', include("django.contrib.auth.urls"))

]
