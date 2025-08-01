from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from api import views
from .views import *


urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('register/', views.RegisterView.as_view()),
    path('dashboard/', views.dashboard),
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", OTPVerificationView.as_view(), name="password-reset-verify-otp"),  # New API
    path("password-reset/change-password/", PasswordResetView.as_view(), name="password-reset-change"),
]