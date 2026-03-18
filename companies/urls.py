from django.urls import path
from .views import *


urlpatterns = [
    path("register/", CompanyRegisterView.as_view()),
    path("<int:id>/status/", CompanyStatusUpdateView.as_view()),
    path("me/update/", CompanyUpdateMeView.as_view()),
    path("create/users/", CompanyUserCreateView.as_view()),
    path("employees/", CompanyEmployeeListView.as_view()),
    path("employees/filter/", CompanyEmployeeFilterView.as_view()),
    path("employees/<int:employee_id>/", EmployeeDetailView.as_view()),
    path("employees/<int:user_id>/update/", CompanyEmployeeUpdateView.as_view()),
    path("employees/<int:user_id>/delete/", CompanyEmployeeDeleteView.as_view()),
    path("update/", UpdateCompanyView.as_view()),
    path("employees/update/", UpdateMyProfile.as_view()),
    path("me/", MeView.as_view()),
    path("get/employees/", MyCompanyEmployeesView.as_view(), name="my-company-employees"),
    path("employee/self-update/", EmployeeSelfFullUpdateView.as_view(), name="employee-self-update"),
    path("employee/delete/<int:user_id>/", EmployeeDeleteView.as_view(), name="employee-delete"),
    path("employee-search/", EmployeeListByTypeView.as_view(), name="employee-list-by-type"),

]