from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "face_core"

urlpatterns = [

    path('add_face/', views.add_face, name='add_face'),
    path('add_face_src/', views.add_face_src, name='add_face_src'),

    path('auth_face/', views.auth_face, name='auth_face'),
    path('auth_face_src/', views.auth_face_src, name='auth_face_src'),

]