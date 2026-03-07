import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from apps.orders.forms import OrderForm, ProductFormSet
from apps.orders.models import Order, OrderStatusChoices


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


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(ordered_by=self.request.user).prefetch_related(
            "products"
        )


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = "orders/form.html"
    success_url = reverse_lazy("orders:list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("New Order")
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
        form.instance.status = OrderStatusChoices.SAVED
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
        return Order.objects.filter(ordered_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Edit Order")
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
        form.instance.status = OrderStatusChoices.SAVED
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
        return Order.objects.filter(ordered_by=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, _("Order deleted successfully."))
        return super().form_valid(form)
