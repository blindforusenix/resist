from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone


# Create your views here.
def index(request):
    return render(request, 'booth/booth_base.html', {})
    #context_object_name  = ''
