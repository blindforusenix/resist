from django.urls import path

from . import views

app_name = 'registrar'
urlpatterns = [
    path('regvoter/', views.regvoter, name='register'),
]
