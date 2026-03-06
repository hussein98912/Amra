from rest_framework import viewsets, permissions
from .models import Package
from .serializers import PackageSerializer


class PackageViewSet(viewsets.ModelViewSet):

    serializer_class = PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not hasattr(self.request.user, "company") or self.request.user.company is None:
            return Package.objects.none()

        return Package.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        user = self.request.user

        if not hasattr(user, "company") or user.company is None:
            raise PermissionError("User has no company assigned")

        serializer.save(
            company=user.company,
            status="DRAFT"
        )