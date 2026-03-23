from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import PermissionDenied

from .models import Package
from .serializers import PackageSerializer
from .filters import PackageFilter
from .permissions import PackagePermission


class PackageViewSet(viewsets.ModelViewSet):
    serializer_class = PackageSerializer
    permission_classes = [PackagePermission]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = PackageFilter

    search_fields = ["title", "description", "hotel_name", "hotel_location"]
    ordering_fields = ["price", "start_date", "created_at", "hotel_stars"]

    def get_queryset(self):
        user = self.request.user

        # Superuser → all packages
        if user.is_superuser:
            return Package.objects.all().order_by("-created_at")

        # Company → only their packages
        if user.is_authenticated and user.role == "COMPANY":
            return Package.objects.filter(company=user.company).order_by("-created_at")

        # Pilgrim → only ACTIVE
        return Package.objects.filter(status="ACTIVE").order_by("-created_at")

    def perform_create(self, serializer):
        user = self.request.user

        if not (user.is_superuser or user.role == "COMPANY"):
            raise PermissionDenied("Only company owners can create packages")

        if user.role == "COMPANY":
            serializer.save(company=user.company, status="DRAFT")
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user

        if user.role == "COMPANY":
            serializer.save(status=self.get_object().status)
        else:
            serializer.save()


