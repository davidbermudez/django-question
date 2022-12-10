from django.urls import path, include, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('init', views.init, name='init'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('registration/<slug:course_slug>/', views.registration, name='registration'),
    #re_path(r'^registration/(?P<slug>[-\w]*)/$', views.registration, name='registration')
]