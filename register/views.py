from django.shortcuts import render
from django.http import HttpResponse

from django.core import serializers
import json
from bulletin.models import Election, RegistrationTeller, Voter
# Create your views here.
def create(request):
    election_data = serializers.serialize('json', Election.objects.all())
    return render(request, 'register/create.html', {
        'election' : election_data
    })
