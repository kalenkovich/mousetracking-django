from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.router, dict(is_test=False), name='router'),
    path('test/', views.router, dict(is_test=True), name='router_test'),
    re_path(r'(?:test/)?get_new_trial_settings/', views.get_new_trial_settings, name='get_new_trial_settings'),
    re_path(r'(?:test/)?save_trial_results/', views.save_trial_results, name='save_trial_results'),
]
