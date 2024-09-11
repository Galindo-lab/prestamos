from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from prestamos.views import OrderAuthorize, SettingsView, OrderHistoryListView, OrderListView, ReportListView, \
    CancelOrderView
from prestamos.views import OrderCreateView
from prestamos.views import OrderDetailView
from prestamos.views import ReportCreateView

urlpatterns = [
    # login y logout
    path(route='', name='login', view=LoginView.as_view(template_name='login.html')),
    path('logout/', LogoutView.as_view(), name='logout'),

    # vistas
    path('items/', OrderCreateView.as_view(), name='order_create'),
    path('items/<str:category>', OrderCreateView.as_view(), name='order_create'),

    path('orders/history/', OrderHistoryListView.as_view(), name='order_history_list'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('reports/', ReportListView.as_view(), name='report_list'),

    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/authorize/<int:pk>/', OrderAuthorize.as_view(), name='order_aprove'),
    path('orders/report/<int:pk>/', ReportCreateView.as_view(), name='order_report'),
    path('orders/cancel/<int:pk>', CancelOrderView.as_view(), name="order_cancel"),

    path('settings', SettingsView.as_view(), name='settings')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
