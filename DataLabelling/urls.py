from django.urls import path

from DataLabelling import views

urlpatterns = [
    path('main/', views.main, name='main'),
    path('wave_table/', views.wave_table, name='wave_table'),
    path('wave_pic/', views.wave_pic, name='wave_pic'),
    path('wave_label/', views.wave_label, name='wave_label'),
]