from django.urls import path

from apps.orders import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="list"),
    path("create/", views.OrderCreateView.as_view(), name="create"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.OrderUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.OrderDeleteView.as_view(), name="delete"),
]
