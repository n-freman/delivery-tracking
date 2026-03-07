from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.products.models import Product


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_type", "payment_type")
        widgets = {
            "delivery_type": forms.Select(attrs={"class": "form-control"}),
            "payment_type": forms.Select(attrs={"class": "form-control"}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("title", "image", "amount", "expected_price", "notes")
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": _("Product title")}
            ),
            "amount": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "expected_price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.0001"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": _("Optional notes"),
                }
            ),
        }


ProductFormSet = inlineformset_factory(
    Order,
    Product,
    form=ProductForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
