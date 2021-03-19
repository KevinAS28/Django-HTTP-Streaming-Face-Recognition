from django.contrib import admin
from django.urls import path, include
from . import add_face, auth_face

app_name = "face_core"

urlpatterns = [

    path('add_face/', add_face.add_face, name='add_face'),
    path('add_face_src/', add_face.add_face_src, name='add_face_src'),
    path('add_face_success/', add_face.add_face_src, name='add_face_success'),
    path('check_add_face/', add_face.check_add_face, name='check_add_face'),

    path('auth_face/', auth_face.auth_face, name='auth_face'),
    path('auth_face_src/', auth_face.auth_face_src, name='auth_face_src'),
    path('auth_face_success/', auth_face.auth_face_src, name='auth_face_success'),
    path('check_auth_face/', auth_face.check_auth_face, name='check_auth_face'),    

]