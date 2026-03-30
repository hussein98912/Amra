from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

router = DefaultRouter()

router.register("admin/pilgrims", PilgrimViewSet, basename="admin-pilgrims")
router.register("admin/companies", CompanyViewSet, basename="admin-companies")
router.register("admin/bookings", AdminBookingViewSet, basename="admin-bookings")
router.register("admin/employees", AdminCompanyEmployeesView, basename="admin-employees")


urlpatterns = router.urls + [
    path("superuser/me/", SuperuserInfoAPIView.as_view(), name="superuser-me"),
    path("admin/employee/<int:id>/", AdminEmployeeDetailView.as_view(), name="admin-employee-detail"),
    path("admin/company/<int:id>/", AdminCompanyDetailView.as_view(), name="admin-company-detail"),
    path("admin/pilgrim/<int:id>/", AdminPilgrimDetailView.as_view(), name="admin-pilgrim-detail"),
    path("companies/<int:company_id>/approve-reject/", CompanyApproveRejectView.as_view()),
    path("packages/<int:package_id>/update-status/", PackageStatusUpdateView.as_view(), name="package-update-status"),
    path("admin/platform-staff/create/",CreatePlatformStaffView.as_view(),name="create-platform-staff"),
    path("admin/platform-staff/<int:staff_id>/",ManagePlatformStaffView.as_view(),name="manage-platform-staff"),
    path("admin/staff/finance/", FinanceEmployeesView.as_view(), name="finance-staff"),
    path("admin/staff/support/", SupportEmployeesView.as_view(), name="support-staff"),
    path("admin/users/<int:user_id>/status/", AdminUserStatusUpdateView.as_view()),
]