from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("pilgrim/register/", PilgrimRegisterView.as_view()),
    path("<int:user_id>/approve/", ApproveUserView.as_view()),
]