from django.urls import path, include
from main import views



urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name='results'),
    path('login/', views.login, name='login'),
    path('save_results/', views.save_results, name='save_results'),
    path('run_diagnosis_script/', views.run_diagnosis_script, name='run_diagnosis_script'),
    path('accounts/', include('django.contrib.auth.urls')),
]