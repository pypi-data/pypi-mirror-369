from django.urls import path
from . import views

urlpatterns = [
    path('console/', views.console_html, name='console'),
]
