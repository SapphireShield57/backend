from django import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    list_users,
    LoginView,
    ForgotPasswordView,
    ResetPasswordVerifyView,
    ResetPasswordSaveView,
    request_verification,
    verify_registration,
    delete_user
)

# Optional: Register ViewSets here if needed
router = DefaultRouter()

urlpatterns = [
    # 🔍 User management
    path('list/', list_users),

    # 🔐 Registration + verification
    path('request/', request_verification),             # Step 1: Request email verification
    path('verify/', verify_registration),               # Step 2: Submit code + password to create user

    # 🔑 Auth
    path('login/', LoginView.as_view()),                # Login with email + password

    # 🔁 Forgot password
    path('forgot-password/', ForgotPasswordView.as_view()),     # Step 1: send code
    path('verify-reset/', ResetPasswordVerifyView.as_view()),  # Step 2: check code
    path('new-password/', ResetPasswordSaveView.as_view()),       # Step 3: set new password
    path('delete/<int:user_id>/', delete_user),


    # 🚪 Any ViewSets (router views)
    path('', include(router.urls)),
]

# ✅ Append registered routes (even if empty for now)
urlpatterns += router.urls
