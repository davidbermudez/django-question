from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import Course, Registration, Question, QuizIntent, QuizFinalized
from .forms import CsvUploadForm, OneQuestionForm, QuizInit
import datetime, csv, random, json
from django.core import serializers
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from django.db.models import Q
import pprint
from django.core.exceptions import PermissionDenied


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
                            question_explanation = row['EXPLICACION'],
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
def init_quiz(request, course_slug):
    user = None
    if request.user.is_authenticated:
        user = request.user
    course = get_object_or_404(Course, course_slug=course_slug)
    if request.method == 'POST':        
        print(request.POST)
        # Evitar crear un nuevo intent por refresco de la página
        # recabar los datos de la selección de temas
        select_theme = request.POST.getlist('select_theme')
        select_random = request.POST.get('select_random')
        select_number = int(request.POST.get('select_number'))
        try:
            questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
            question_active = questionsList.quizintent_active
        except Exception as e:
            print("Error:", e)
            # Correcto, no existe            
            if select_random == None:
                select_random = False
            else:
                select_random = True
            result=createIntent(user, course, select_theme, select_random, select_number, request)
            if result == None:
                return redirect('course', course_slug=course_slug)
            questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
            question_active = '0'
            # Message
            messages.add_message(request, messages.INFO, '<strong>Recuerde:</strong><br/>Preguntas correctas: 1 pt<br/>Preguntas incorrectas: -1 pt<br/>Preguntas no contestadas: 0 pts', extra_tags='is-info')
    else:
        questionsList = QuizIntent.objects.get(quizintent_user=user, quizintent_course=course)
        question_active = questionsList.quizintent_active
        select_random = questionsList.quizintent_random
    #convert a dict/list
    questionsResponses = json.loads(questionsList.quizintent_responses)
    questionsQuestions = json.loads(questionsList.quizintent_questions)
    indice = int(question_active)
    list_random = [1, 2, 3, 4]
    if select_random:
        list_random = random.sample(list_random, 4)    
    return render(request, 'course/quiz.html', {
        'course': course,
        'question': question_active,
        'indice': indice,
        'questionsList': questionsQuestions, #questionsList.quizintent_questions
        'questionsResponses' : questionsResponses,
        'questionResponse': questionsResponses[indice],
        'listRandom': list_random
    })


@login_required
def retry_quiz(request, quizfinalized_id):
    url = request.META['HTTP_REFERER']
    print(url)
    user = None
    if request.user.is_authenticated:
        user = request.user
        try:
            quizfinalized = QuizFinalized.objects.get(quizfinalized_user=user, id=quizfinalized_id)
        except QuizFinalized.DoesNotExist:
            messages.add_message(request, messages.ERROR, 'Error al recuperar el test', extra_tags='is-danger')
            return HttpResponseRedirect(url)
        # trasladar datos desde QuizFinalized a QuizIntent
        questionintent = QuizIntent.objects.filter(quizintent_user=user)
        if len(questionintent)==0:
            list_responses = (None,None,None,None,None,None,None,None,None,None)
            new_record = QuizIntent(
                quizintent_user=user,
                quizintent_course=quizfinalized.quizfinalized_course,
                quizintent_questions=quizfinalized.quizfinalized_questions,
                quizintent_responses=json.dumps(list_responses),
                quizintent_active='0'
            )
            new_record.save()
            messages.add_message(request, messages.INFO, 'Ahora puede reintentar el cuestionario', extra_tags='is-info')            
            url = reverse('init_quiz', args=(quizfinalized.quizfinalized_course.course_slug,))
            return HttpResponseRedirect(url)            
            '''
            return render(request, 'course/quiz.html', {
                'course': new_record.quizintent_course,
                'question': 0,
                'indice': 0,
                'questionsList': new_record.quizintent_questions, #questionsList.quizintent_questions
                'questionsResponses' : new_record.quizintent_responses,
                'questionResponse': None
            })
            '''
        else:
            messages.add_message(request, messages.WARNING, 'Ya existe un intento si finalizar. Acabe primero el cuestionario', extra_tags='is-warnning')
    else:
        raise PermissionDenied()


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
            'quizid': questionsList.id
        })
    else:
        raise PermissionDenied()


def createIntent(user_object, course_object, select_theme, select_random, select_number, request):
    '''
    create a list with 10 question random and save in database
    '''
    if len(select_theme)==0:
        # All Themes
        questions = Question.objects.filter(question_course=course_object).order_by('?')[:10]
    else:
        questions = Question.objects.filter(question_course=course_object, question_theme__in=select_theme).order_by('?')[:select_number]
    # create Object database
    list_responses = []
    for i in range(select_number):
        list_responses.append(None)
    #list_responses = (None,None,None,None,None,None,None,None,None,None)
    serialized_lre = serializers.serialize('json', questions)
    new_record = QuizIntent(
        quizintent_user=user_object,
        quizintent_course=course_object,
        quizintent_questions=serialized_lre,
        quizintent_responses=json.dumps(list_responses),
        quizintent_active='0',
        quizintent_random=select_random
    )
    new_record.save()
    return 1


@login_required
def question_edit(request, pk):
    """_summary_

    Args:
        request (request): objet content http var session
        pk (_type_): id Question Model

    Raises:
        PermissionDenied: _description_
        PermissionDenied: _description_

    Returns:
        Response: _description_
    """
    user = None
    if request.user.is_authenticated:
        user = request.user
        if not user.is_staff:
            raise PermissionDenied()
        # Tiene permisos, continuar
        if request.method == 'POST':
            form = OneQuestionForm(request.POST)
            if form.is_valid():
                print(request.POST)
                question_update=Question.objects.get(id=pk)
                question_update.question_text = form.cleaned_data['question_text']
                question_update.question_response1 = form.cleaned_data['question_response1']
                question_update.question_response2 = form.cleaned_data['question_response2']
                question_update.question_response3 = form.cleaned_data['question_response3']
                question_update.question_response4 = form.cleaned_data['question_response4']
                question_update.question_explanation = form.cleaned_data['question_explanation']
                question_update.question_valid = int(form.cleaned_data['question_valid'])
                question_update.save()                
                messages.add_message(request, messages.SUCCESS, 'Pregunta Actualizada', extra_tags='is-success')
                # Ahora, vamos a tratar de actualizar todos los QuizFinalized que contengan esta pregunta, actualizando si procede, también el resultado del test
                updateResultsFinalized(question_update)
            else:
                messages.add_message(request, messages.ERROR, 'Error formulario', extra_tags='is-danger')
            url = form.cleaned_data['referer']
            return HttpResponseRedirect(url)
        else:
            if request.META['HTTP_REFERER']:
                referer = request.META['HTTP_REFERER']
            else:
                raise PermissionDenied()
            question = Question.objects.get(id=pk)            
            form = OneQuestionForm(instance=question)            
        return render(request, 'course/question_edit.html', {
            'form': form,
            'question': question,
            'referer': referer,
        })


def updateResultsFinalized(question):
    print("Question", question)    
    n = question.id
    print("Question", n)
    # Search regular expresion: pk\": XXXX 
    string_search = r'pk\\\":[[:blank:]]' + str(n)
    resultados = QuizFinalized.objects.filter(quizfinalized_questions__regex=string_search)
    for r in resultados:
        quizfinalized_questions = {}
        quizfinalized_questions = json.loads(r.quizfinalized_questions)        
        # localizar la pregunta dentro del intento finalizado:
        for t in quizfinalized_questions:
            if t['pk']==n:
                # Localizado!! cambiar valores antiguos por los nuevos
                t['fields']['question_text']=question.question_text
                t['fields']['question_response1']=question.question_response1
                t['fields']['question_response2']=question.question_response2
                t['fields']['question_response3']=question.question_response3
                t['fields']['question_response4']=question.question_response4
                t['fields']['question_explanation']=question.question_explanation
                t['fields']['question_valid']=question.question_valid
        # reconvertir a JSON y guardar objeto Quizfinalized
        new_quizfinalized_questions = json.dumps(quizfinalized_questions)
        r.quizfinalized_questions = new_quizfinalized_questions
        r.save()
    for r in resultados:
        respuestas = json.loads(r.quizfinalized_responses)
        preguntas = json.loads(r.quizfinalized_questions)
        i = 0
        ptos = 0
        nc = 0
        aciertos = 0
        errores = 0
        success = []
        for p in respuestas:
            pregunta = preguntas[i]['fields']['question_valid']
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
            i = i + 1
        r.quizfinalized_result = ptos
        r.quizfinalized_success = json.dumps(success)
        r.save()


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
    """_summary_

    Args:
        request (_type_): _description_

    Returns:
        _type_: _description_
    """
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