from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from prestamos.views import CancelOrderView
from prestamos.views import OrderAuthorize
from prestamos.views import OrderCreateView
from prestamos.views import OrderDetailView
from prestamos.views import OrderHistoryListView
from prestamos.views import OrderListView
from prestamos.views import ReportCreateView
from prestamos.views import ReportListView
from prestamos.views import ScheduleView
from prestamos.views import SettingsView, DeliverOrderView, ReturnOrderView, RejectOrderView
from prestamos.views import UserProfileView

urlpatterns = [

    # login y logout
    path(route='', view=LoginView.as_view(template_name='login.html'), name='login'),
    path(route='logout/', view=LogoutView.as_view(), name='logout'),

    path(route='orders/', view=OrderListView.as_view(), name='order_list'),
    path(route='orders/history/', view=OrderHistoryListView.as_view(), name='order_history_list'),
    path(route='orders/<int:pk>/', view=OrderDetailView.as_view(), name='order_detail'),

    path(route='order/<int:pk>/deliver/', view=DeliverOrderView.as_view(), name='deliver_order'),
    path(route='order/<int:pk>/return/', view=ReturnOrderView.as_view(), name='return_order'),
    path(route='order/<int:pk>/reject/', view=RejectOrderView.as_view(), name='reject_order'),
    path(route='orders/<int:pk>/authorize/', view=OrderAuthorize.as_view(), name='order_aprove'),
    path(route='orders/<int:pk>/report/', view=ReportCreateView.as_view(), name='order_report'),
    path(route='orders/<int:pk>/cancel', view=CancelOrderView.as_view(), name="order_cancel"),

    path(route='reports/', view=ReportListView.as_view(), name='report_list'),
    path(route='items/', view=OrderCreateView.as_view(), name='order_create'),
    path(route='items/<str:category>', view=OrderCreateView.as_view(), name='order_create'),

    path(route='settings', view=SettingsView.as_view(), name='settings'),
    path(route='schedule', view=ScheduleView.as_view(), name='schedule'),
    path(route='profile/', view=UserProfileView.as_view(), name='user_profile'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
