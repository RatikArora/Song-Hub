from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('loading/', views.loading, name='loading'),
    path('loading2/', views.loading2, name='loading2'),
    path('download/<int:i>/', views.download, name='download'),

]