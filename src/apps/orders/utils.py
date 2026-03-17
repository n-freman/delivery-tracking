from decimal import Decimal

from constance import config

from apps.orders.models import PaymentTypeChoices


def get_exchange_rate(payment_type: str) -> Decimal:
    if payment_type == PaymentTypeChoices.HALF:
        return Decimal(str(config.CNY_TO_TMT_HALF))
    return Decimal(str(config.CNY_TO_TMT_FULL))


def calculate_totals(order) -> dict:
    rate = get_exchange_rate(order.payment_type)
    products = list(order.products.filter(include_in_order=True))

    total_expected_cny = sum(p.expected_price * p.amount for p in products)

    total_actual_cny = sum(
        (p.actual_price if p.actual_price is not None else p.expected_price) * p.amount
        for p in products
    )

    return {
        "rate": rate,
        "products": products,
        "total_expected_cny": total_expected_cny,
        "total_actual_cny": total_actual_cny,
        "total_expected_tmt": total_expected_cny * rate,
        "total_actual_tmt": total_actual_cny * rate,
        "has_actual": any(p.actual_price is not None for p in products),
    }
