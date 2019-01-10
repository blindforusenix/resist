from django.shortcuts import render

# Create your views here.
def create(request):
    return render(request, 'register/create.html', {})
    #context_object_name  = ''
