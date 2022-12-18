from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Registration, Question, QuizIntent
from .forms import CsvUploadForm, OneQuestionForm
import datetime, csv, random, json
from django.core import serializers


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
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)    
    return render(request, 'course/course.html', {
        'course': course,
    })


@login_required
def csv_upload(request, course_slug):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    if request.method == 'POST':
        form = CsvUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['csvFile'])

            with open('temporal.csv', 'r') as archivo:
                read = csv.DictReader(archivo)
                d = False
                for row in read:
                    if d:                        
                        new_record = Question(
                            question_theme=row['MATERIA'],
                            question_chapter = row['TEMA'],
                            question_text = row['PREGUNTA'],
                            question_response1 = row['RESPUESTA1'],
                            question_response2 = row['RESPUESTA2'],
                            question_response3 = row['RESPUESTA3'],
                            question_response4 = row['RESPUESTA4'],
                            question_valid = row['CORRECTA'],
                            question_course = course
                        )
                        new_record.save()
                    d = True
            return HttpResponseRedirect('/course/{course_slug}/')
    else:
        form = CsvUploadForm()
    return render(request, 'course/csv_upload.html', {
        'course': course,
        'form': form
    })


def handle_uploaded_file(f):
    with open('temporal.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@login_required
def init(request):
    '''if not request.user.is_authenticated:
        return render(request, 'registration/login.html')'''
    return render(request, 'index.html', {
        'article': 1,
    })


@login_required
def init_quiz(request, course_slug, ordinal=0):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    if request.method == 'POST':
        print("hola")
    else:
        # Buscamos en la base de datos el intento anterior para este usuario
        try:
            questionsList = QuizIntent.objects.get(quizintent_user=user)
            question_active = questionsList.quizintent_active            
        except QuizIntent.DoesNotExist:
            # Si no existe, preparamos un conjunto de 10 preguntas al azar desde Question        
            createIntent(user, course)
            questionsList = QuizIntent.objects.get(quizintent_user=user)            
            question_active = '0'            
        #convert a dict/list
        questionsResponses = json.loads(questionsList.quizintent_responses)
        questionsQuestions = json.loads(questionsList.quizintent_questions)
        indice = int(question_active)
    return render(request, 'course/quiz.html', {
        'course': course,
        'question': question_active,
        'indice': indice,
        'questionsList': questionsQuestions, #questionsList.quizintent_questions
        'questionsResponses' : questionsResponses,
        'questionResponse': questionsResponses[indice]
    })


def createIntent(user_object, course_object):
    '''
    create a list with 10 question random and save in database
    '''    
    # cargamos las preguntas de ese curso, desordenadas al azar
    questions = Question.objects.filter(question_course=course_object).order_by('?')[:10]
    # create Object database
    list_responses = (None,None,None,None,None,None,None,None,None,None)
    serialized_lre = serializers.serialize('json', questions)
    new_record = QuizIntent(
        quizintent_user=user_object,
        quizintent_questions=serialized_lre,
        quizintent_responses=json.dumps(list_responses),
        quizintent_active='0'
    )
    new_record.save()
    

def processOption(request):
    if request.is_ajax():
        user = None
        if request.user.is_authenticated:
            user = request.user        
            # Realizar cálculos o consultar la base de datos aquí
            quizIntent = QuizIntent.objects.get(quizintent_user=user)
            quizIntent.quizintent_active = request.POST.get('key')
            quizIntent.save()
            result = {'result': 'Success'}
            return JsonResponse(result)    
    return HttpResponseBadRequest()


def sendOption(request):
    if request.is_ajax():
        user = None
        if request.user.is_authenticated:
            user = request.user        
            # Realizar cálculos o consultar la base de datos aquí
            quizIntent = QuizIntent.objects.get(quizintent_user=user)
            pregunta = request.POST.get('key')
            respuesta = request.POST.get('value')
            indice = int(pregunta)
            #convert a dict
            provisional = json.loads(quizIntent.quizintent_responses)
            #provisional = list(provisional)
            #print("Tipo:", type(provisional))
            #provisional = list(provisional)
            #print("Tipo:", type(provisional))
            #print(provisional)
            #print("nº", indice)
            #print(provisional[indice])
            #cambiar elemento
            provisional[indice] = respuesta
            #convert a json
            quizintent_responses = json.dumps(provisional)
            quizIntent.quizintent_responses = quizintent_responses
            quizIntent.save()
            result = {'result': 'Success'}
            return JsonResponse(result)    
    return HttpResponseBadRequest()