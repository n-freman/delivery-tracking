import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order


class Product(models.Model):
    short_id = models.CharField(
        max_length=8,
        verbose_name=_("Short ID"),
        editable=False,
    )
    image = models.ImageField(
        upload_to="products",
        verbose_name=_("image"),
        help_text=_("Product image file."),
    )
    amount = models.PositiveIntegerField(
        default=1,
        verbose_name=_("amount"),
        help_text=_("Quantity of this product in the order."),
    )
    expected_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name=_("expected price"),
        help_text=_("The anticipated price of the product before confirmation."),
    )
    actual_price = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("actual price"),
        help_text=_(
            "The final confirmed price of the product. Leave blank if not yet known."
        ),
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("notes"),
        help_text=_("Any additional notes or remarks about this product."),
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("order"),
        help_text=_("The order this product belongs to."),
    )
    link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("product link"),
        help_text=_("Link to the product page (e.g. Taobao, 1688, etc.)"),
    )
    include_in_order = models.BooleanField(
        default=True,
        verbose_name=_("include in order"),
        help_text=_(
            "Whether this product should be included when processing the order."
        ),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-updated_at", "-created_at"]
        indexes = [
            models.Index(fields=["include_in_order"], name="product_include_idx"),
        ]

    def __str__(self):
        return _("%(short_id)s (x%(amount)s)") % {
            "short_id": self.short_id,
            "amount": self.amount,
        }

    def save(self, *args, **kwargs):
        if not self.short_id:
            self.short_id = secrets.token_urlsafe(4).upper()[:6]
        super().save(*args, **kwargs)
