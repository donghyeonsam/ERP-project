from django.urls import path
from . import views

urlpatterns = [
    # 1. Expense
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),

    # 2. AccountsReceivable
    path('accounts-receivable/', views.accounts_receivable_list, name='accounts_receivable_list'),
    path('accounts-receivable/<int:pk>/', views.accounts_receivable_detail, name='accounts_receivable_detail'),

    # 3. AccountsPayable
    path('accounts-payable/', views.accounts_payable_list, name='accounts_payable_list'),
    path('accounts-payable/<int:pk>/', views.accounts_payable_detail, name='accounts_payable_detail'),
]