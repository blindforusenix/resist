from django.shortcuts import render

# Create your views here.
def check(request):
    return render(request, 'bulletin/check.html', {})
    #context_object_name  = ''
