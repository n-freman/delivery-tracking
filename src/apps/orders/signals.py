from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from apps.orders.models import Order, OrderStatusChoices
from apps.general.telegram import send_telegram_message


@receiver(post_save, sender=Order)
def notify_admin_on_order_save(sender, instance, created, **kwargs):
    if instance.status != OrderStatusChoices.SAVED:
        return

    text = (
        f"📦 <b>Заказ получен/обновлен</b>\n\n"
        f"🆔 Номер заказа: <code>{instance.public_id}</code>\n"
        f"👤 Пользователь: {instance.ordered_by}\n"
        f"🚚 Доставка: {instance.get_delivery_type_display()}\n"
        f"💳 Оплата: {instance.get_payment_type_display()}\n"
        f"📋 Количество товаров: {instance.products.count()}\n"
    )
    send_telegram_message(settings.TELEGRAM_ADMIN_CHAT_ID, text)
