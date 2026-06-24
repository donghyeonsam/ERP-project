from django.urls import path
from . import views

urlpatterns = [
    path('salaries/', views.salary_list, name='salary_list'),
    path('salaries/<int:pk>/', views.salary_detail, name='salary_detail'),

    path('bonuses/', views.bonus_list, name='bonus_list'),
    path('bonuses/<int:pk>/', views.bonus_detail, name='bonus_detail'),

    path('year-end-settlements/', views.yearend_list, name='yearend_list'),
    path('year-end-settlements/<int:pk>/', views.yearend_detail, name='yearend_detail'),

    path('severances/', views.severance_list, name='severance_list'),
    path('severances/<int:pk>/', views.severance_detail, name='severance_detail'),
]
