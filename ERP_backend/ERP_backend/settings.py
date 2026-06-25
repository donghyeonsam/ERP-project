"""
Django settings for ERP_backend project.
- dj-rest-auth + simplejwt(JWT) 인증
- 회원가입(dj-rest-auth.registration + allauth): 사원번호로 가입
- 전역 IsAuthenticated / Vue 개발서버용 CORS
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
# load_dotenv(BASE_DIR / '.env')

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# GMS(SSAFY API 게이트웨이) — OpenAI 호환 엔드포인트를 GMS_KEY로 호출한다.
# .env 파일(ERP_backend/.env, git에 커밋되지 않음)에서 로드
GMS_KEY = os.environ.get('GMS_KEY')
GMS_BASE_URL = 'https://gms.ssafy.io/gmsapi/api.openai.com/v1'
GMS_MODEL = 'gpt-5.4-nano'

SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])


INSTALLED_APPS = [
    # --- Django 기본 ---
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',              # allauth 필수 (추가됨)

    # --- 3rd party ---
    'channels',
    'rest_framework',
    'rest_framework.authtoken',          # dj-rest-auth 의존성
    # 'rest_framework_simplejwt.token_blacklist',  # (선택) 로그아웃 토큰 무효화
    'dj_rest_auth',
    'dj_rest_auth.registration',         # 회원가입 (추가됨)
    'allauth',                           # (추가됨)
    'allauth.account',                   # (추가됨)
    'allauth.socialaccount',             # (추가됨, 소셜 안 써도 같이 두는 게 무난)
    'corsheaders',
    'django_filters',

    # --- local apps ---
    'employees',
    'procurement',
    'finance',
    'messages.apps.MessagesConfig',      # ※ apps.py 에서 label='erp_messages' 필수
    'works',
    'ssafy_international',
    'logistics',
    'inventory',
    'payroll',
    'analytics',
]

SITE_ID = 1                              # django.contrib.sites (추가됨)

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',   # allauth 필수 (추가됨)
]

ROOT_URLCONF = 'ERP_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ERP_backend.wsgi.application'
ASGI_APPLICATION = 'ERP_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =====================================================================
# 인증 백엔드 (allauth 추가됨)
# =====================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


# =====================================================================
# Django REST Framework
# =====================================================================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}


# =====================================================================
# dj-rest-auth
# =====================================================================
REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_COOKIE': 'erp-access',
    'JWT_AUTH_REFRESH_COOKIE': 'erp-refresh',
    'JWT_AUTH_HTTPONLY': False,
    # 사원번호 회원가입용 커스텀 시리얼라이저 (추가됨)
    'JWT_AUTH_COOKIE_SECURE': True,       # ← 추가
    'JWT_AUTH_COOKIE_SAMESITE': 'None',   # ← 추가
    'REGISTER_SERIALIZER': 'employees.serializers.EmployeeRegisterSerializer',
}


# =====================================================================
# allauth 회원가입 설정 (신버전 문법 / 추가됨)
#  - 아이디(username) + 비밀번호로 로그인
#  - 가입 폼 필드: username, password1, password2 (email 안 받음)
#  - 이메일 인증 비활성화 (사내 ERP라 불필요)
# =====================================================================
ACCOUNT_LOGIN_METHODS = {'username'}
ACCOUNT_SIGNUP_FIELDS = ['username*', 'password1*', 'password2*', 'email']
ACCOUNT_EMAIL_VERIFICATION = 'none'


# =====================================================================
# simplejwt 토큰 수명
# =====================================================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}


# =====================================================================
# CORS — Vue 개발 서버 허용
# =====================================================================
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:5173',
    'http://127.0.0.1:5173',
])
CORS_ALLOW_CREDENTIALS = True


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = False

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================================================================
# 배포 환경 쿠키 / CSRF 설정
# =====================================================================
CSRF_TRUSTED_ORIGINS = [
    'https://glistening-twilight-831e13.netlify.app',
]

SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SECURE = True

REST_AUTH_TOKEN_COOKIE_SECURE = True