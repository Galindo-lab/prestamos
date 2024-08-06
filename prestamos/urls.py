from django.urls import path

from prestamos.views import OrderCreateView, OrderListView, OrderDetailView

urlpatterns = [
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]