from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Course, Registration, Question, QuizIntent, QuizFinalized
from .forms import CsvUploadForm, OneQuestionForm, QuizInit
import datetime, csv, random, json
from django.core import serializers
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Count,Avg
import pprint


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
    #cursos = Registration.objects.filter(registration_user=user)
    return render(request, 'index.html', {
        'courses': cursos,
    })


@login_required
def registration(request, course_slug):
    course = get_object_or_404(Course, course_slug=course_slug)
    # Si ya está matriculado no hacer nada
    try:
        verify = Registration.objects.get(
            registration_user=request.user,
            registration_course=course
        )
    except Registration.DoesNotExist:
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
    #Eliminar los Intents de este usuario y curso
    intentos = QuizIntent.objects.filter(quizintent_user=user, quizintent_course=course).delete()
    return redirect('index')


def privacy(request):
    return render(request, 'privacy.html', {        
    })


@login_required
def course(request, course_slug):
    page = request.GET.get('page', 1)
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    # Intent en vigor?
    quizintent = None
    quizintent = QuizIntent.objects.filter(quizintent_user=user, quizintent_course=course)
    quizfinalized = None
    quizfinalized = QuizFinalized.objects.filter(quizfinalized_user=user, quizfinalized_course=course).order_by("quizfinalized_dateEnd")
    paginator = Paginator(quizfinalized, per_page=5)
    intentos = paginator.page(page)
    ac = []
    er = []
    nc = []
    for i in intentos:
        aciertos = errores = nocontesta = 0
        #print(i)        
        #print(i.quizfinalized_success)
        resp = json.loads(i.quizfinalized_success)
        for j in resp:
            if j == True:
                aciertos = aciertos + 1
            elif j == False:
                errores = errores + 1
            else:
                nocontesta = nocontesta + 1
        #    print("J:", j)
        #print("Ac:", aciertos)
        #print("Er:", errores)
        #print("Nc:", nocontesta)
        ac.append(aciertos)
        er.append(errores)
        nc.append(nocontesta)
    
    # Enviar form 
    form = QuizInit()
    # combo de  temas
    temas = Question.objects.filter(question_course=course).values('question_theme').distinct().order_by('question_theme')
    return render(request, 'course/course.html', {
        'course': course,
        'intents': quizintent,
        'finalized': intentos,
        'aciertos': ac,
        'errores': er,
        'nocontesta': nc,
        'themes': temas,
        'form': form
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
            
            try:
                with open('temporal.csv', 'r') as archivo:
                    read = csv.DictReader(archivo)
                    a = 0
                    for row in read:                       
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
                        a = a + 1
            except:
                messages.add_message(request, messages.ERROR, 'Error al procesar el archivo')
                return redirect('index')
            messages.add_message(request, messages.INFO, 'Procesadas ' + str(a) + ' preguntas nuevas')
            url = reverse('course', args=(course_slug,))
            return HttpResponseRedirect(url)
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
def init_quiz(request, course_slug, section='<all>'):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    if request.method == 'POST':        
        print(request.POST)
        # recabar los datos de la selección de temas
        select_theme = request.POST.getlist('select_theme')
        result=createIntent(user, course, select_theme, request)
        if result == None:
            return redirect('course', course_slug=course_slug)
        questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
        question_active = '0'
        # Message
        messages.add_message(request, messages.INFO, '<strong>Recuerde:</strong><br/>Preguntas correctas: 1 pt<br/>Preguntas incorrectas: -1 pt<br/>Preguntas no contestadas: 0 pts', extra_tags='is-info')
    else:
        questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
        question_active = questionsList.quizintent_active
        '''
        # Buscamos en la base de datos el intento anterior para este usuario
        try:
            questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
            question_active = questionsList.quizintent_active            
        except QuizIntent.DoesNotExist:
            # Si no existe, preparamos un conjunto de 10 preguntas al azar desde Question
            createIntent(user, course, section)            
            questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)            
            question_active = '0'
            # Message
            messages.add_message(request, messages.INFO, '<strong>Recuerde:</strong><br/>Preguntas correctas: 1 pt<br/>Preguntas incorrectas: -1 pt<br/>Preguntas no contestadas: 0 pts', extra_tags='is-info')
        '''
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


@login_required
def result_quiz(request, course_slug, quizfinalized_id):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    questionsList = QuizFinalized.objects.get(quizfinalized_user=user, id=quizfinalized_id)
    questionsResponses = json.loads(questionsList.quizfinalized_responses)
    questionsQuestions = json.loads(questionsList.quizfinalized_questions)
    questionsSuccess = json.loads(questionsList.quizfinalized_success)
    return render(request, 'course/result.html', {
        'course': course,
        'questionsQuestions': questionsQuestions,
        'questionsResponses' : questionsResponses,
        'questionsSuccess' : questionsSuccess,
    })


def createIntent(user_object, course_object, select_theme, request):
    '''
    create a list with 10 question random and save in database
    '''    
    # cargamos las preguntas de ese curso, desordenadas al azar
    questions = Question.objects.filter(question_course=course_object, question_chapter__in=select_theme).order_by('?')[:10]
    if len(questions)==0:
        messages.add_message(request, messages.ERROR, '<strong>Error al extraer las preguntas</strong>', extra_tags='is-danger')
        return None
    print("Preguntas", questions)
    # create Object database    
    list_responses = (None,None,None,None,None,None,None,None,None,None)
    serialized_lre = serializers.serialize('json', questions)
    new_record = QuizIntent(
        quizintent_user=user_object,
        quizintent_course=course_object,
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
            course_id = request.POST.get('id')
            # Realizar cálculos o consultar la base de datos aquí
            quizIntent = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course_id)
            quizIntent.quizintent_active = request.POST.get('key')
            quizIntent.save()
            result = {'result': 'Success'}
            return JsonResponse(result)    
    return HttpResponseBadRequest()


def sendOption(request):
    print('Request', request.POST)
    if request.is_ajax():
        user = None
        if request.user.is_authenticated:
            user = request.user                    
            pregunta = request.POST.get('key')
            respuesta = request.POST.get('value')
            course_id = request.POST.get('id')
            # Realizar cálculos o consultar la base de datos aquí
            quizIntent = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course_id)
            print('R', respuesta)
            indice = int(pregunta)
            #convert a dict
            provisional = json.loads(quizIntent.quizintent_responses)
            #cambiar elemento
            if respuesta=='0':
                respuesta = None
            provisional[indice] = respuesta
            #convert a json
            quizintent_responses = json.dumps(provisional)
            quizIntent.quizintent_responses = quizintent_responses
            quizIntent.save()
            result = {'result': 'Success0'}
            if respuesta == None:
                result = {'result': 'Success1'}
            return JsonResponse(result)    
    return HttpResponseBadRequest()


def endQuiz(request):
    if request.is_ajax():
        user = None
        if request.user.is_authenticated:
            user = request.user
            # Debe de haber un intento activo, localizar, trasladar los datos a la table definitiva y eliminar            
            course_id = request.POST.get('id')            
            try:
                quizintent = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course_id)
                respuestas = json.loads(quizintent.quizintent_responses)
                preguntas = json.loads(quizintent.quizintent_questions)
                i = 0
                ptos = 0
                nc = 0
                aciertos = 0
                errores = 0
                success = []
                for p in respuestas:
                    pregunta = preguntas[i]['fields']['question_valid']
                    print("Pregunta", type(pregunta))
                    print("Respuesta",type(p))                    
                    if p == None:
                        ptos = ptos
                        success.append(None)
                        nc = nc + 1
                    elif p == str(pregunta):
                        ptos = ptos + 1
                        success.append(True)
                        aciertos = aciertos + 1
                    else:
                        ptos = ptos - 1
                        success.append(False)
                        errores = errores + 1
                    #print("Pregunta: ", preguntas[i]['fields']['question_valid'])
                    #print("Respuesta: ", p)
                    i = i + 1                
                
                quizfinalized = QuizFinalized(
                    quizfinalized_user = quizintent.quizintent_user,
                    quizfinalized_course = quizintent.quizintent_course,
                    quizfinalized_questions = quizintent.quizintent_questions,
                    quizfinalized_responses = quizintent.quizintent_responses,
                    quizfinalized_result = ptos,
                    quizfinalized_success = json.dumps(success),
                    quizfinalized_dateInit = quizintent.quizintent_dateInit
                )
                quizfinalized.save()
                quizintent.delete()
                texto = 'Ha obtenido <strong>' + str(ptos) + '</strong> puntos<br/>' + \
                    '<ul><li>Aciertos:<strong>' + str(aciertos) + '</strong></li>' + \
                    '<li>Errores:<strong>' + str(errores) + '</strong></li>' + \
                    '<li>No contestadas:<strong>' + str(nc) + '</strong></li></ul>'
                if ptos > 0:
                    tipo = messages.INFO
                else:
                    tipo = messages.ERROR
                messages.add_message(request, tipo, texto)
                result = {'result': 'Success'}
                return JsonResponse(result)
            except QuizIntent.DoesNotExist:
                print('Error')
    return HttpResponseBadRequest()