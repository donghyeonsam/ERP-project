from django.urls import path
from . import views

urlpatterns = [
    # 1. Vehicle
    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),

    # 2. Dispatch
    path('dispatches/', views.dispatch_list, name='dispatch_list'),
    path('dispatches/<int:pk>/', views.dispatch_detail, name='dispatch_detail'),
]
