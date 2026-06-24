from django.urls import path
from . import views

urlpatterns = [
    path('demand-insight/', views.demand_insight, name='demand_insight'),
]
