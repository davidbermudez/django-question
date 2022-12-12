from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Registration
import datetime

# Create your views here.
def index(request):    
    user = None
    if request.user.is_authenticated:
        user = request.user

    courses = Course.objects.all()    
    cursos = []
    for course in courses:
        try:
            registration = Registration.objects.get(
                registration_user=user,
                registration_course=course.id
            )
            course_render = {
                'course_name':course.course_name,
                'course_type':course.course_type.type_name,
                'course_slug':course.course_slug,
                'registration_date':registration.registration_date,
                'registration_date_end':registration.registration_date_end
            }
        except Registration.DoesNotExist:
            course_render = {
                'course_name':course.course_name,
                'course_type':course.course_type,
                'course_slug':course.course_slug,
                'registration_date':None,
                'registration_date_end':None
            }                 
        cursos.append(course_render)
    return render(request, 'index.html', {
        'courses': cursos,
    })

@login_required
def registration(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    new_record = Registration(
        registration_user=request.user,
        registration_course=course,        
    )
    new_record.save()    
    return redirect('index')


@login_required
def unsubscribe(request, course_slug):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    registration = Registration.objects.get(
        registration_user=user,
        registration_course=course.id
    )
    registration.delete()
    return redirect('index')


@login_required
def course(request, course_slug):
    cursos = []
    return render(request, 'index.html', {
        'courses': cursos,
    })


@login_required
def init(request):
    '''if not request.user.is_authenticated:
        return render(request, 'registration/login.html')'''
    return render(request, 'index.html', {
        'article': 1,
    })