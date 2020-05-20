from django.urls import path
from . import views

urlpatterns = [
    path('', views.router, name='router'),
    path('get_new_trial_settings/', views.get_new_trial_settings, name='get_new_trial_settings'),
    path('save_trial_results/', views.save_trial_results, name='save_trial_results'),
]
