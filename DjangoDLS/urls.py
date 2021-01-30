"""DjangoDLS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from DjangoDLS import views, settings

urlpatterns = [
    path('', views.index),
    url(r'index/(?P<file_url>.*)', views.index, name='index'),
    path('file/', views.save_file, name='file_save'),
    url(r'result_by_id/(?P<file_id>.*)', views.check_result, name='check_result'),
    url(r'get_file/(?P<file>.*)', views.get_file, name='file_get'),
    url(r'get_by_id/(?P<file_id>.*)', views.get_file_by_id, name='file_by_id')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()