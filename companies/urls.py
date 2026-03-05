from django.urls import path
from .views import (
    CompanyRegisterView,
    CompanyStatusUpdateView,
    CompanyMeView,
    CompanyUpdateMeView
)

urlpatterns = [
    path("register/", CompanyRegisterView.as_view()),
    path("<int:id>/status/", CompanyStatusUpdateView.as_view()),
    path("me/", CompanyMeView.as_view()),
    path("me/update/", CompanyUpdateMeView.as_view()),
]