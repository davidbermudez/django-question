from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('init', views.init, name='init'),
    path('processOption/', views.processOption, name='processOption'),
    path('privacy/', views.privacy, name='privacy'),
    path('sendOption/', views.sendOption, name='sendOption'),
    path('endQuiz/', views.endQuiz, name='endQuiz'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('registration/<slug:course_slug>/', views.registration, name='registration'),
    path('unsubscribe/<slug:course_slug>/', views.unsubscribe, name='unsubscribe'),
    path('course/<slug:course_slug>/', views.course, name='course'),
    path('csv_upload/<slug:course_slug>/', views.csv_upload, name='csv_upload'),
    path('init_quiz/<slug:course_slug>/', views.init_quiz, name='init_quiz'),
    path('init_quiz/<slug:course_slug>/', views.init_quiz, name='init_quiz'),
    path('result_quiz/<slug:course_slug>/<int:quizfinalized_id>', views.result_quiz, name='result_quiz'),
    #re_path(r'^registration/(?P<slug>[-\w]*)/$', views.registration, name='registration')
]