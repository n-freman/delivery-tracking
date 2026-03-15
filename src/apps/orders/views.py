import secrets

from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from apps.general.telegram import send_telegram_message
from apps.orders.forms import OrderForm, ProductFormSet
from apps.orders.models import Order, OrderStatusChoices, PaymentTypeChoices
from apps.orders.utils import calculate_totals


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/list.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        return (
            Order.objects.filter(ordered_by=self.request.user)
            .prefetch_related("products")
            .order_by("-id")
        )


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/form.html"
    success_url = reverse_lazy("orders:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Order")
        context["rate_full"] = config.CNY_TO_TMT_FULL
        context["rate_half"] = config.CNY_TO_TMT_HALF
        if self.request.POST:
            context["product_formset"] = ProductFormSet(
                self.request.POST, self.request.FILES
            )
        else:
            context["product_formset"] = ProductFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        product_formset = context["product_formset"]

        form.instance.ordered_by = self.request.user
        form.instance.public_id = secrets.token_urlsafe(6).upper()
        form.instance.status = OrderStatusChoices.ON_REVIEW
        if product_formset.is_valid():
            self.object = form.save()
            product_formset.instance = self.object
            product_formset.save()
            messages.success(self.request, _("Order created successfully."))
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/form.html"
    success_url = reverse_lazy("orders:list")

    def get_queryset(self):
        return Order.objects.filter(
            ordered_by=self.request.user,
            status__in=[OrderStatusChoices.ON_REVIEW, OrderStatusChoices.REVIEWED],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Order")
        context["rate_full"] = config.CNY_TO_TMT_FULL
        context["rate_half"] = config.CNY_TO_TMT_HALF
        if self.request.POST:
            context["product_formset"] = ProductFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )
        else:
            context["product_formset"] = ProductFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        product_formset = context["product_formset"]
        form.instance.status = OrderStatusChoices.ON_REVIEW
        if product_formset.is_valid():
            self.object = form.save()
            product_formset.instance = self.object
            product_formset.save()
            messages.success(self.request, _("Order updated successfully."))
            return redirect(self.success_url)

        return self.render_to_response(self.get_context_data(form=form))


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = "orders/confirm_delete.html"
    success_url = reverse_lazy("orders:list")
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(
            ordered_by=self.request.user,
            status__in=[OrderStatusChoices.ON_REVIEW, OrderStatusChoices.REVIEWED],
        )

    def form_valid(self, form):
        messages.success(self.request, _("Order deleted successfully."))
        return super().form_valid(form)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(ordered_by=self.request.user).prefetch_related(
            "products"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["totals"] = calculate_totals(self.object)
        context["can_confirm"] = self.object.status == OrderStatusChoices.REVIEWED
        return context


class OrderConfirmView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(
            Order,
            pk=pk,
            ordered_by=request.user,
            status=OrderStatusChoices.REVIEWED,
        )

        order.status = OrderStatusChoices.ORDERED
        order.save()

        totals = calculate_totals(order)

        text = (
            f"✅ <b>Заказ подтверждён пользователем</b>\n\n"
            f"🆔 Номер заказа: <code>{order.public_id}</code>\n"
            f"👤 Пользователь: {order.ordered_by}\n"
            f"🚚 Доставка: {order.get_delivery_type_display()}\n"
            f"💳 Оплата: {order.get_payment_type_display()}\n\n"
            f"💰 Итого (ожидаемая цена): {totals['total_expected_cny']:.2f} ¥ "
            f"= {totals['total_expected_tmt']:.2f} TMT\n"
        )

        if totals["has_actual"]:
            text += (
                f"💰 Итого (фактическая цена): {totals['total_actual_cny']:.2f} ¥ "
                f"= {totals['total_actual_tmt']:.2f} TMT\n"
            )

        text += f"📊 Курс: {totals['rate']} TMT/¥\n"
        print("Sending telegram notification", settings.TELEGRAM_ADMIN_CHAT_ID)
        send_telegram_message(settings.TELEGRAM_ADMIN_CHAT_ID, text)

        messages.success(
            request,
            _("Your order %(id)s has been confirmed and sent for processing.")
            % {"id": order.public_id},
        )
        return redirect("orders:detail", pk=pk)
