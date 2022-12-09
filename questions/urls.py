from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('init', views.init, name='init'),
    path('accounts/', include('django.contrib.auth.urls')),
]