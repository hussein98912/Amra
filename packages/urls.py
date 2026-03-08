from rest_framework.routers import DefaultRouter
from .views import PackageViewSet

router = DefaultRouter()
router.register(r'packages', PackageViewSet, basename='packages')

urlpatterns = router.urls