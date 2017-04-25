"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from .views import login, search
from blog.views import choose_website

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',choose_website),
    url(r'^todos/',include('todo.urls')),
    url(r'^users/',include('users.urls')),
    url(r'^blog/',include('blog.urls')),
    url(r'^accounts/profile/',login),
    url(r'search/$',search),
    url(r'^tags/',include('tags.urls'))
]
