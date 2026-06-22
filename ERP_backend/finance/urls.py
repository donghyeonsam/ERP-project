from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF 라우터 초기화
router = DefaultRouter()

# 각각의 ViewSet을 URL 엔드포인트에 등록
router.register(r'expenses', views.ExpenseViewSet, basename='expense')
router.register(r'accounts-receivable', views.AccountsReceivableViewSet, basename='accountsreceivable')
router.register(r'accounts-payable', views.AccountsPayableViewSet, basename='accountspayable')

# 메인 프로젝트 urls.py가 "api/v1/finance/"로 이 파일을 연결(include)하므로,
# 최종 API 주소는 자동으로 매핑됩니다.
urlpatterns = [
    path('', include(router.urls)),
]