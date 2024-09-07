# views.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import OrderForm, AuthorizeForm, OrderItemFormSet, ReporteForm
from .models import Order, Report, Item, Category, OrderStatusChoices


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = "settings.html"


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'report_list.html'
    context_object_name = 'orders'
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user, 
            order_date__gt=timezone.now(), 
            status__in=[OrderStatusChoices.PENDING, OrderStatusChoices.APPROVED]
        )
        

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user,
            order_date__gt=timezone.now(),
            status__in=[OrderStatusChoices.DELIVERED],
        )


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReporteForm
    template_name = 'report_create.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.user = self.request.user

        pk = self.kwargs.get('pk')  # pk de la orden en la url
        form.instance.order = get_object_or_404(Order, pk=pk)

        return super().form_valid(form)


class OrderAuthorize(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = AuthorizeForm
    template_name = 'order_authorize.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.approved_by = self.request.user
        return super().form_valid(form)


class OrderCreateView(LoginRequiredMixin, View):
    select_item_template = 'order_form.html'
    change_date_template  = 'order_confirm.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.select_item_template, {
            'order_form': OrderForm(),
            'item_formset': OrderItemFormSet(),
            'items': Item.objects.all(),
            'categories': Category.objects.all()
        })
    

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        order = None
            
        if order_form.is_valid() and item_formset.is_valid():
            try:
                # hacer la orden 
                order = self.transaction_order(request)
                
            except Exception as e:
                # Buscar horario alternativo el mismo día
                alternative_time = self.find_alternative_time(item_formset, order_form.cleaned_data['order_date'])
                if alternative_time:
                    start_time, end_time = alternative_time
                    messages.error(request, f"{e}. Horario alternativo disponible: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
                else:
                    messages.error(request, f"{e}. No se encontraron horarios alternativos el mismo día.")
                
                return render(request, self.change_date_template, {
                    'item_formset': item_formset,
                    'order_form': order_form
                }) 
                
            else:
                # redirigir a la pagina de detalles de la orden
                messages.success(request, "La orden se ha creado exitosamente.")
                return redirect('order_detail', order.pk)
            
        # Si los formularios no son válidos, mostrar de nuevo el formulario
        return render(request, self.change_date_template, {
            'item_formset': item_formset,
            'order_form': order_form
        }) 
                    
                    
    def transaction_order(self, request) -> Order:
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        
        with transaction.atomic():
            # agregar unidades a la orden
            order_form.instance.user = self.request.user
            order = order_form.save()

            for item_form in item_formset:
                if item_form.is_valid(): 
                    item = item_form.cleaned_data['item']
                    quantity = item_form.cleaned_data['quantity']

                    if quantity < 0:
                        # si solicito 0 unidades del articulo ignorar
                        continue

                    order.add_item(item, quantity)

            if order.units.count() <= 0:
                raise ValueError("La orden no tiene unidades")
        
        return order
    
    def find_alternative_time(self, item_formset, order_date):
        """
        Busca un horario alternativo para todos los artículos en el mismo día.
        :param item_formset: Formset de artículos seleccionados.
        :param order_date: Fecha de inicio de la orden.
        :return: Un horario alternativo (start_time, end_time) o None si no hay disponibilidad.
        """
        end_date = order_date.replace(hour=23, minute=59)  # Limitar la búsqueda al mismo día
        for form in item_formset:
            if form.is_valid():
                item = form.cleaned_data['item']
                quantity = form.cleaned_data['quantity']
                alternative = item.find_alternative_availability(order_date, end_date)
                if not alternative:
                    return None  # Si algún artículo no tiene disponibilidad, retornar None
        return alternative  # Retorna el primer horario alternativo disponible para todos
                    
                    
                    
                    

class OrderHistoryListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_history_list.html'
    context_object_name = 'orders'

    # agregar esto a una configuracion del sistema
    paginate_by = 100

    def get_queryset(self):
        # ordenes del usuario que ya hayan pasado
        return Order.objects.filter(
            user=self.request.user, 
            order_date__lt=timezone.now()
        )


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
