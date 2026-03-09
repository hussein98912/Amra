from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()

router.register("admin/pilgrims", PilgrimViewSet, basename="admin-pilgrims")
router.register("admin/companies", CompanyUsersViewSet, basename="admin-companies")
router.register("admin/bookings", AdminBookingViewSet, basename="admin-bookings")

urlpatterns = router.urls