from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    return render(request, 'index.html', {
        'article': 1,
    })

'''(login_url='/accounts/login/')'''
@login_required
def init(request):
    '''if not request.user.is_authenticated:
        return render(request, 'registration/login.html')'''
    return render(request, 'index.html', {
        'article': 1,
    })