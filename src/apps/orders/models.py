from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class DeliveryTypeChoice(models.TextChoices):
    AVIA = "AVIA", _("Avia")
    EXPRESS = "EXPRESS", _("Express")
    AUTO = "AUTO", _("Auto")


class PaymentTypeChoices(models.TextChoices):
    HALF = "HALF", _("Half")
    FULL = "FULL", _("Full")


class OrderStatusChoices(models.TextChoices):
    ON_REVIEW = "ON_REVIEW", _("On review")
    REVIEWED = "REVIEWED", _("Reviewed")
    ORDERED = "ORDERED", _("Ordered")
    DELIVERED = "DELIVERED", _("Delivered")


class Order(models.Model):
    ordered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        related_name="orders",
        verbose_name=_("ordered by"),
        help_text=_("The user who placed this order."),
    )
    public_id = models.CharField(
        max_length=16,
        verbose_name=_("public ID"),
        help_text=_(
            "A unique public-facing identifier for this order (max 16 characters)."
        ),
    )
    delivery_type = models.CharField(
        max_length=16,
        choices=DeliveryTypeChoice,
        default=DeliveryTypeChoice.AUTO,
        verbose_name=_("delivery type"),
        help_text=_("The method used to deliver this order (Avia, Express, or Auto)."),
    )
    payment_type = models.CharField(
        max_length=16,
        choices=PaymentTypeChoices,
        default=PaymentTypeChoices.FULL,
        verbose_name=_("payment type"),
        help_text=_("Whether the order is paid in full or in two installments (Half)."),
    )
    status = models.CharField(
        max_length=16,
        choices=OrderStatusChoices,
        default=OrderStatusChoices.ON_REVIEW,
        verbose_name=_("status"),
        help_text=_("Current processing status of the order."),
    )

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["public_id"], name="order_public_id_idx"),
            models.Index(fields=["status"], name="order_status_idx"),
        ]

    def __str__(self):
        return _("Order %(public_id)s by %(user)s") % {
            "public_id": self.public_id,
            "user": self.ordered_by,
        }
