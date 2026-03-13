from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path

router = DefaultRouter()

router.register("admin/pilgrims", PilgrimViewSet, basename="admin-pilgrims")
router.register("admin/companies", CompanyUsersViewSet, basename="admin-companies")
router.register("admin/bookings", AdminBookingViewSet, basename="admin-bookings")
router.register("admin/employees", AdminCompanyEmployeesView, basename="admin-employees")


urlpatterns = router.urls + [
    path("admin/employee/<int:id>/", AdminEmployeeDetailView.as_view(), name="admin-employee-detail"),
    path("admin/company/<int:id>/", AdminCompanyDetailView.as_view(), name="admin-company-detail"),
    path("admin/pilgrim/<int:id>/", AdminPilgrimDetailView.as_view(), name="admin-pilgrim-detail"),
]