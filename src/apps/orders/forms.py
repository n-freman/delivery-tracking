from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory
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
        fields = ("link", "image", "amount", "expected_price", "notes")
        widgets = {
            "link": forms.URLInput(
                attrs={"class": "form-control", "placeholder": "https://..."}
            ),
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


class ProductBaseFormSet(BaseInlineFormSet):
    def _should_delete_form(self, form):
        return super()._should_delete_form(form)

    def full_clean(self):
        super().full_clean()

    def _clean_form(self):
        pass


ProductFormSet = inlineformset_factory(
    Order,
    Product,
    form=ProductForm,
    formset=ProductBaseFormSet,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
)
