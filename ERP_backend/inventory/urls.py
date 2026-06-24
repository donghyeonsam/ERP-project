from django.urls import path
from . import views

urlpatterns = [
    path('count-plans/', views.count_plan_list, name='count_plan_list'),
    path('count-plans/<int:pk>/', views.count_plan_detail, name='count_plan_detail'),

    path('count-items/', views.count_item_list, name='count_item_list'),
    path('count-items/<int:pk>/', views.count_item_detail, name='count_item_detail'),
]
