from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('result/<int:app_id>/', views.application_result, name='application_result'),
    path('test/<int:app_id>/', views.take_test, name='take_test'),
    path('test/evaluate/<int:app_id>/', views.evaluate_test, name='evaluate_test'),
    path('dashboard/', views.company_dashboard, name='dashboard'),
]
