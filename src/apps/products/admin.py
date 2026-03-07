from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.products.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "order",
        "amount",
        "expected_price",
        "actual_price",
        "include_in_order",
    )
    list_filter = ("include_in_order",)
    search_fields = ("title", "order__public_id")
    ordering = ("title",)
    fieldsets = (
        (_("General"), {"fields": ("title", "image", "order")}),
        (_("Pricing"), {"fields": ("expected_price", "actual_price")}),
        (_("Additional"), {"fields": ("amount", "include_in_order", "notes")}),
    )
