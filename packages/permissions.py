from rest_framework.permissions import BasePermission, SAFE_METHODS


class PackagePermission(BasePermission):

    def has_permission(self, request, view):

        # GET allowed for all authenticated + public
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):

        user = request.user

        # ⭐ Superuser full access
        if user.is_superuser:
            return True

        # ⭐ Company owner can edit/delete but NOT status
        if user.role == "COMPANY":
            return obj.company == user.company

        return False