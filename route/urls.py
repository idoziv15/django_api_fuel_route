from django.urls import path
from . import views

urlpatterns = [
    path('get-route/', views.get_route, name='get_route'),
]