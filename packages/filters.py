import django_filters
from .models import Package

class PackageFilter(django_filters.FilterSet):
    # فلترة حسب الشركة
    company_id = django_filters.NumberFilter(field_name="company__id", lookup_expr="exact")

    # فلترة حسب نوع الباقة
    package_type = django_filters.CharFilter(field_name="package_type", lookup_expr="iexact")

    # فلترة حسب السعر من وإلى
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # فلترة حسب الحالة
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    # فلترة حسب تاريخ البداية
    start_date_after = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_before = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = Package
        fields = [
            "company_id",
            "package_type",
            "status",
            "min_price",
            "max_price",
            "start_date_after",
            "start_date_before",
        ]