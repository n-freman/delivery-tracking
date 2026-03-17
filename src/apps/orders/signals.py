from constance import config
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from apps.general.telegram import (send_telegram_media_group,
                                   send_telegram_message)
from apps.orders.models import Order, OrderStatusChoices


def _build_product_lines(order) -> str:
    products = order.products.all()
    if not products.exists():
        return "  — нет товаров\n"

    lines = ""
    for p in products:
        lines += f"\n  📎 <b>{p.short_id}</b>\n"
        if p.link:
            lines += f"     🔗 <a href='{p.link}'>Ссылка на товар</a>\n"
        lines += f"     💵 Ожид. цена: {p.expected_price} ¥\n"
        if p.actual_price:
            lines += f"     💰 Факт. цена: {p.actual_price} ¥\n"
        if p.notes:
            lines += f"     📝 Примечание: {p.notes}\n"
    return lines


def _collect_image_urls(order) -> list[str]:
    base_url = config.BASE_URL.rstrip("/")
    if not base_url:
        return []
    return [f"{base_url}{p.image.url}" for p in order.products.all() if p.image]


@receiver(post_save, sender=Order)
def notify_admin_on_order_save(sender, instance, created, **kwargs):
    print("Notifying admin")
    if instance.status != OrderStatusChoices.ON_REVIEW:
        return

    print("Status check passed")
    product_lines = _build_product_lines(instance)

    text = (
        f"📦 <b>{'Новый заказ' if created else 'Заказ обновлён'}</b>\n\n"
        f"🆔 Номер заказа: <code>{instance.public_id}</code>\n"
        f"👤 Пользователь: {instance.ordered_by}\n"
        f"🚚 Доставка: {instance.get_delivery_type_display()}\n"
        f"💳 Оплата: {instance.get_payment_type_display()}\n"
        f"📋 Товаров: {instance.products.count()}\n"
        f"\n🛒 <b>Состав заказа:</b>{product_lines}"
    )

    image_urls = _collect_image_urls(instance)

    if image_urls:
        send_telegram_message(text)
        send_telegram_media_group(image_urls)
    else:
        send_telegram_message(text)


@receiver(post_save, sender=Order)
def notify_admin_on_order_approve(sender, instance, created, **kwargs):
    print("Notifying admin order")
    if instance.status != OrderStatusChoices.ORDERED:
        return

    print("Status check passed order")
    product_lines = _build_product_lines(instance)

    text = (
        "📦 <b>Заказ подтверждён!</b>\n\n"
        f"🆔 Номер заказа: <code>{instance.public_id}</code>\n"
        f"👤 Пользователь: {instance.ordered_by}\n"
        f"🚚 Доставка: {instance.get_delivery_type_display()}\n"
        f"💳 Оплата: {instance.get_payment_type_display()}\n"
        f"📋 Товаров: {instance.products.count()}\n"
        f"\n🛒 <b>Состав заказа:</b>{product_lines}"
    )

    image_urls = _collect_image_urls(instance)

    if image_urls:
        send_telegram_message(text)
        send_telegram_media_group(image_urls)
    else:
        send_telegram_message(text)
