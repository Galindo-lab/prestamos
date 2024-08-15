from django.urls import path

from prestamos.views import OrderAuthorize
from prestamos.views import ReportCreateView
from prestamos.views import OrderCreateView
from prestamos.views import OrderDetailView
from prestamos.views import OrderListView

urlpatterns = [
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/authorize/<int:pk>/', OrderAuthorize.as_view(), name='order_aprove'),
    path('orders/report/<int:pk>/', ReportCreateView.as_view(), name='order_report'),
]
