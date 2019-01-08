from django.shortcuts import render

from bulletin/models import Voter
# Create your views here.
def regvoter(request):
    voter = Voter.object.get(name="request.body.name")
    return render(request, 'booth/regvoter.html', {

    })
