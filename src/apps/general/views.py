from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.orders.models import Order


@login_required
def index(request):
    recent_orders = (
        Order.objects.filter(ordered_by=request.user)
        .prefetch_related("products")
        .order_by("-id")[:5]
    )
    context = {
        "recent_orders": recent_orders,
    }
    return render(request, "general/index.html", context)


def handler404(request, exception):
    return render(request, "404.html", status=404)
