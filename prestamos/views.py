# views.py

import math
from datetime import timedelta
from random import shuffle

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
        return super().form_valid(form)


class OrderCreateView(LoginRequiredMixin, View):
    select_item_template = 'order_form.html'
    change_date_template = 'order_confirm.html'

    def get(self, request, category=None, *args, **kwargs):

        if category:
            category_obj = get_object_or_404(Category, name=category)
            items = category_obj.items.all()
        else:
            items = Item.objects.all()

        return render(request, self.select_item_template, {
            'order_form': OrderForm(),
            'item_formset': OrderItemFormSet(),
            'items': items,
            'categories': Category.objects.all()
        })

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        alternative_slots = []

        if order_form.is_valid() and item_formset.is_valid():
            try:
                # Try to create the order
                order = self.transaction_order(request)


            except Exception as e:
                alternative_slots = self.suggest_alternatives(order_form, item_formset)

                if alternative_slots:
                    # Añadir el mensaje de error con las alternativas
                    messages.error(request, f"{e}. Horarios Alterativos:")
                else:
                    messages.error(request, f"{e}. No se encontraron horarios alternativos.")

            else:
                messages.success(request, "La orden se ha creado exitosamente.")
                return redirect('order_detail', order.pk)

        # Si el formulario es inválido
        return render(request, self.change_date_template, {
            'item_formset': item_formset,
            'order_form': order_form,
            'alternative_slots': alternative_slots
        })

    def transaction_order(self, request) -> Order:
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        with transaction.atomic():
            # Create the order and add units
            order_form.instance.user = self.request.user
            order = order_form.save()

            for item_form in item_formset:
                if item_form.is_valid():
                    item = item_form.cleaned_data['item']
                    quantity = item_form.cleaned_data['quantity']
                    order_date = order_form.cleaned_data['order_date']
                    return_date = order_form.cleaned_data['return_date']

                    if quantity < 0:
                        # Skip if quantity is less than 0
                        continue

                        # order.add_item(item, quantity)
                    units = item.units_available(order_date, return_date)

                    if quantity > len(units):  # Veríficar que hay suficientes unidades
                        raise Exception("No hay suficientes unidades de '" + str(item.name) + "' diponibles")

                    shuffle(units)  # revolver los elementos de la lista
                    order.units.add(*(units[:quantity]))  # agregar la cantidad de unidades especificadas

            if order.units.count() <= 0:
                raise ValueError("La orden no tiene unidades disponibles.")

        return order

    def suggest_alternatives(self, order_form, item_formset):
        """
        Sugiere alternativas de horarios donde TODOS los artículos solicitados estén disponibles simultáneamente.
        """
        order_date = order_form.cleaned_data['order_date']
        return_date = order_form.cleaned_data['return_date']

        max_alternatives = 3  # Limitar a 3 alternativas
        alternatives = []

        # Inicializamos un rango de búsqueda en el tiempo original de la orden
        current_start_time = order_date
        duration = return_date - order_date
        time_increment = timedelta(
            minutes=math.ceil(duration.total_seconds() / 60))  # Incremento de 1 hora en la búsqueda

        # Limitar el tiempo máximo de búsqueda a 24 horas adicionales
        max_search_time = order_date + timedelta(days=1)

        while current_start_time < max_search_time and len(alternatives) < max_alternatives:
            all_items_available = True

            for item_form in item_formset:
                if not item_form.is_valid():
                    continue

                item = item_form.cleaned_data['item']
                quantity = item_form.cleaned_data['quantity']

                if quantity < 1:
                    continue

                # Verificar si el artículo tiene suficientes unidades disponibles en el intervalo actual
                available_units = item.units_available(current_start_time, current_start_time + duration)
                if len(available_units) < quantity:
                    all_items_available = False
                    break  # Si uno de los artículos no tiene suficientes unidades, pasamos a la siguiente iteración

            if all_items_available:
                # Si todos los artículos están disponibles en este intervalo, añadimos la alternativa
                alternatives.append({
                    'start_time': current_start_time,
                    'end_time': current_start_time + duration
                })

            # Incrementamos el tiempo de búsqueda en una hora
            current_start_time += time_increment

        return alternatives


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
