from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from apps.orders.models import Order, DeliveryTypeChoice, PaymentTypeChoices, OrderStatusChoices
from apps.products.models import Product

User = get_user_model()


class OrderModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.order = Order.objects.create(
            ordered_by=self.user,
            public_id="ORD-0001",
            delivery_type=DeliveryTypeChoice.AUTO,
            payment_type=PaymentTypeChoices.FULL,
            status=OrderStatusChoices.ON_REVIEW,
        )

    # --- Creation ---

    def test_order_created_successfully(self):
        self.assertIsNotNone(self.order.pk)

    def test_order_default_delivery_type(self):
        order = Order.objects.create(
            ordered_by=self.user,
            public_id="ORD-0002",
            status=OrderStatusChoices.ON_REVIEW,
        )
        self.assertEqual(order.delivery_type, DeliveryTypeChoice.AUTO)

    def test_order_default_payment_type(self):
        order = Order.objects.create(
            ordered_by=self.user,
            public_id="ORD-0003",
            status=OrderStatusChoices.ON_REVIEW,
        )
        self.assertEqual(order.payment_type, PaymentTypeChoices.FULL)

    def test_order_default_status(self):
        order = Order.objects.create(
            ordered_by=self.user,
            public_id="ORD-0004",
        )
        self.assertEqual(order.status, OrderStatusChoices.ON_REVIEW)

    # --- Field values ---

    def test_order_public_id(self):
        self.assertEqual(self.order.public_id, "ORD-0001")

    def test_order_delivery_type_choices(self):
        for choice in [DeliveryTypeChoice.AVIA, DeliveryTypeChoice.EXPRESS, DeliveryTypeChoice.AUTO]:
            self.order.delivery_type = choice
            self.order.save()
            self.order.refresh_from_db()
            self.assertEqual(self.order.delivery_type, choice)

    def test_order_payment_type_choices(self):
        for choice in [PaymentTypeChoices.HALF, PaymentTypeChoices.FULL]:
            self.order.payment_type = choice
            self.order.save()
            self.order.refresh_from_db()
            self.assertEqual(self.order.payment_type, choice)

    def test_order_status_choices(self):
        for choice in [OrderStatusChoices.ON_REVIEW, OrderStatusChoices.REVIEWED, OrderStatusChoices.ORDERED]:
            self.order.status = choice
            self.order.save()
            self.order.refresh_from_db()
            self.assertEqual(self.order.status, choice)

    # --- Nullability ---

    def test_ordered_by_can_be_null(self):
        self.order.ordered_by = None
        self.order.save()
        self.order.refresh_from_db()
        self.assertIsNone(self.order.ordered_by)

    def test_ordered_by_set_null_on_user_delete(self):
        self.user.delete()
        self.order.refresh_from_db()
        self.assertIsNone(self.order.ordered_by)

    # --- Relationships ---

    def test_order_related_name(self):
        user = User.objects.create_user(username="user2", password="pass")
        Order.objects.create(ordered_by=user, public_id="ORD-X1", status=OrderStatusChoices.ON_REVIEW)
        Order.objects.create(ordered_by=user, public_id="ORD-X2", status=OrderStatusChoices.ON_REVIEW)
        self.assertEqual(user.orders.count(), 2)

    # --- Meta ---

    def test_verbose_name(self):
        self.assertEqual(Order._meta.verbose_name, _("order"))

    def test_verbose_name_plural(self):
        self.assertEqual(Order._meta.verbose_name_plural, _("orders"))

    def test_ordering(self):
        self.assertEqual(Order._meta.ordering, ["-id"])

    # --- __str__ ---

    def test_str(self):
        expected = "Order ORD-0001 by %s" % self.user
        self.assertIn("ORD-0001", str(self.order))
        self.assertIn(str(self.user), str(self.order))


class ProductModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )
        self.order = Order.objects.create(
            ordered_by=self.user,
            public_id="ORD-0001",
            status=OrderStatusChoices.ON_REVIEW,
        )
        self.product = Product.objects.create(
            title="Test Product",
            image="products/test.jpg",
            amount=3,
            expected_price=Decimal("99.9900"),
            actual_price=Decimal("89.9900"),
            notes="Some notes",
            order=self.order,
            include_in_order=True,
        )

    # --- Creation ---

    def test_product_created_successfully(self):
        self.assertIsNotNone(self.product.pk)

    def test_product_default_amount(self):
        product = Product.objects.create(
            title="Default Amount Product",
            image="products/test.jpg",
            expected_price=Decimal("10.0000"),
            order=self.order,
        )
        self.assertEqual(product.amount, 1)

    def test_product_default_include_in_order(self):
        product = Product.objects.create(
            title="Include Default",
            image="products/test.jpg",
            expected_price=Decimal("10.0000"),
            order=self.order,
        )
        self.assertTrue(product.include_in_order)

    # --- Field values ---

    def test_product_title(self):
        self.assertEqual(self.product.title, "Test Product")

    def test_product_expected_price(self):
        self.assertEqual(self.product.expected_price, Decimal("99.9900"))

    def test_product_actual_price(self):
        self.assertEqual(self.product.actual_price, Decimal("89.9900"))

    def test_product_notes(self):
        self.assertEqual(self.product.notes, "Some notes")

    def test_product_amount(self):
        self.assertEqual(self.product.amount, 3)

    # --- Nullability ---

    def test_actual_price_can_be_null(self):
        self.product.actual_price = None
        self.product.save()
        self.product.refresh_from_db()
        self.assertIsNone(self.product.actual_price)

    def test_notes_can_be_null(self):
        self.product.notes = None
        self.product.save()
        self.product.refresh_from_db()
        self.assertIsNone(self.product.notes)

    # --- Relationships ---

    def test_product_belongs_to_order(self):
        self.assertEqual(self.product.order, self.order)

    def test_product_cascade_delete(self):
        product_pk = self.product.pk
        self.order.delete()
        self.assertFalse(Product.objects.filter(pk=product_pk).exists())

    def test_order_products_related_name(self):
        Product.objects.create(
            title="Second Product",
            image="products/test2.jpg",
            expected_price=Decimal("20.0000"),
            order=self.order,
        )
        self.assertEqual(self.order.products.count(), 2)

    # --- Meta ---

    def test_verbose_name(self):
        self.assertEqual(Product._meta.verbose_name, _("product"))

    def test_verbose_name_plural(self):
        self.assertEqual(Product._meta.verbose_name_plural, _("products"))

    def test_ordering(self):
        self.assertEqual(Product._meta.ordering, ["title"])

    # --- __str__ ---

    def test_str(self):
        result = str(self.product)
        self.assertIn("Test Product", result)
        self.assertIn("3", result)