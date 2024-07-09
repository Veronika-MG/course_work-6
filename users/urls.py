from django.urls import path
from users import views


app_name = "users"


urlpatterns = [
    # Регистрация
    path("registration/form/", views.RegistrationView.as_view(), name="registration_form"),
    path("registration/email/sent/", views.RegistrationEmailSentTemplateView.as_view(), name="registration_email_sent"),
    path("registration/confirmation/<str:uidb64>/<str:token>/", views.RegistrationValidationView.as_view(), name="registration_link"),
    path("registration/confirmation/failed/", views.RegistrationFailedView.as_view(), name="registration_confirmation_failed"),

    # Вход и выход
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/preview/", views.LogoutPreview.as_view(), name="logout_preview"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),

    # Восстановление пароля
    path("reset/form/", views.UserPasswordResetView.as_view(), name="reset_form"),
    path("reset/email/sent/", views.ResetEmailSentTemplateView.as_view(), name="reset_email_sent"),
    path("reset/confirmation/<str:uidb64>/<str:token>/", views.UserPasswordResetConfirmView.as_view(), name="reset_confirm"),
    path("reset/success/", views.ResetCompleteTemplateView.as_view(), name="reset_complete"),

    # crud
    path("update/", views.UserUpdateView.as_view(), name="update"),
    path("detail/", views.UserDetailView.as_view(), name="detail"),

    # manager
    path("manager/deactivate/<int:pk>/", views.ManagerDeactivateUserUpdateView.as_view(), name="manager_deactivate"),
    path("manager/list/", views.ManagerUserListView.as_view(), name="manager_list"),
    path("manager/detail/<int:pk>/", views.ManagerUserDetailView.as_view(), name="manager_detail"),
]
