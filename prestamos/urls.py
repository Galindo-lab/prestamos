from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from prestamos.views import OrderAuthorize
from prestamos.views import ReportCreateView
from prestamos.views import OrderCreateView
from prestamos.views import OrderDetailView
from prestamos.views import OrderListView


urlpatterns = [
    # login
    path(route='login/', name='login', view=LoginView.as_view(
        template_name='login.html'
    )),

    # logout
    path('logout/', LogoutView.as_view(), name='logout'),

    path('', OrderListView.as_view(), name=""),

    path('orders/create/', OrderCreateView.as_view(), name='order_create'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('orders/authorize/<int:pk>/', OrderAuthorize.as_view(), name='order_aprove'),
    path('orders/report/<int:pk>/', ReportCreateView.as_view(), name='order_report'),
]
