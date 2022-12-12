from django.shortcuts import render, get_object_or_404
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
        registration = Registration.objects.filter(
            registration_user=user,
            registration_course=course
        )
        if registration:
            course_render = {
                'course_name':course.course_name,
                'course_type':course.course_type,
                'course_slug':course.course_slug,
                'registration_date':registration.registration_date,
                'registration_date_end':registration.registration_date_end
            }
        else:
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
        #registration_date=datetime.datetime.now().date()
    )
    new_record.save()
    index(request)


@login_required
def init(request):
    '''if not request.user.is_authenticated:
        return render(request, 'registration/login.html')'''
    return render(request, 'index.html', {
        'article': 1,
    })