from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.products.models import Product


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ("title", "amount", "expected_price", "actual_price", "include_in_order")
    verbose_name = _("product")
    verbose_name_plural = _("products")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "public_id",
        "ordered_by",
        "delivery_type",
        "payment_type",
        "status",
    )
    list_filter = ("status", "delivery_type", "payment_type")
    search_fields = ("public_id", "ordered_by__username")
    ordering = ("-id",)
    inlines = [ProductInline]
    fieldsets = (
        (_("General"), {"fields": ("ordered_by", "public_id")}),
        (_("Order Details"), {"fields": ("delivery_type", "payment_type", "status")}),
    )
