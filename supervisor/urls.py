from django.urls import path

from . import views

app_name = 'supervisor'
urlpatterns = [
    #supervisor urls
    path('createelection/', views.createelection, name='createelection'),
    path('addelection/', views.addelection, name='addelection'),
    path('createtabulation/', views.createtabulation, name='createtabulation'),
    path('createauth/', views.createvoter, name='createvoter'),
    path('createvoter/', views.createvoter, name='createvoter'),
    path('regvoter/', views.regvoter, name='register'),
]
