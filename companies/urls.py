from django.urls import path
from .views import *


urlpatterns = [
    path("register/", CompanyRegisterView.as_view()),
    path("<int:id>/status/", CompanyStatusUpdateView.as_view()),
    path("me/", CompanyMeView.as_view()),
    path("me/update/", CompanyUpdateMeView.as_view()),
    path("create/users/", CompanyUserCreateView.as_view()),
    path("employees/", CompanyEmployeeListView.as_view()),
    path("employees/filter/", CompanyEmployeeFilterView.as_view()),
    path("employees/<int:employee_id>/", EmployeeDetailView.as_view()),
    path("employees/<int:user_id>/update/", CompanyEmployeeUpdateView.as_view()),
    path("employees/<int:user_id>/delete/", CompanyEmployeeDeleteView.as_view()),
]