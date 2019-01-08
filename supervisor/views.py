from django.shortcuts import render
from django.http import HttpResponseRedirect
from bulletin.models import Election, Voter
# Create your views here.


def createelection(request):
    return render(request, 'supervisor/createelection.html', {})

def addelection(request):
    election = Election()
    election.name = request.POST['election_name']
    election.organization = request.POST['election_organization']
    election.description = request.POST['election_description']
    election.help_email = request.POST['email']
    #TODO: Change the following to call key generators
    election.public_key = "Filler Public Key"
    election.private_key = "Filler Private Key"
    election.save();
    #TODO: change the redirect URL
    return HttpResponseRedirect(reverse('supervisor:createelection'))

def createvoter(request):
    pass

def createtabulation(request):
    pass

def createauth(request):
    pass

def regvoter(request):
    pass
