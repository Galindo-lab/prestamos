from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from prestamos.views import OrderAuthorize, SettingsView, OrderHistoryListView
from prestamos.views import ReportCreateView
from prestamos.views import OrderCreateView
from prestamos.views import OrderDetailView
# from prestamos.views import OrderListView


urlpatterns = [
    # login
    path(route='', name='', view=LoginView.as_view(
        template_name='login.html'
    )),

        path(route='login/', name='login', view=LoginView.as_view(
        template_name='login.html'
    )),

    # logout
    path('logout/', LogoutView.as_view(), name='logout'),
    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/history', OrderHistoryListView.as_view(), name='order_history_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/authorize/<int:pk>/', OrderAuthorize.as_view(), name='order_aprove'),
    path('orders/report/<int:pk>/', ReportCreateView.as_view(), name='order_report'),
    path('settings', SettingsView.as_view(), name='settings'),
]
