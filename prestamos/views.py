# views.py

import math
from datetime import time, timedelta
from random import shuffle

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, TemplateView
from django.views.generic import DetailView
from django.views.generic import ListView
from extra_settings.models import Setting

from .forms import OrderForm, OrderItemFormSet, ReporteForm
from .models import Order, Report, Item, Category, OrderStatusChoices


class ScheduleView(LoginRequiredMixin, View):
    template = "schedule.html"

    def get(self, request):
        # Renderizar la plantilla con los datos obtenidos directamente desde Setting.get()
        return render(request, self.template, {
            'opening_days': Setting.get("STORE_OPEN_DAYS", default="Indefinido").split(','),  # Días de apertura
            'opening_time': Setting.get("STORE_OPENING_TIME", default=time(0, 0)),  # Horario de apertura
            'closing_time': Setting.get("STORE_CLOSING_TIME", default=time(23, 0)),  # Horario de cierre
            'warehouse_phone': Setting.get("WAREHOUSE_PHONE", default="+00 000000000"),  # Teléfono del almacén
            'warehouse_email': Setting.get("WAREHOUSE_EMAIL", default="warehouse@doe.com"),  # Email del almacén
            'support_phone': Setting.get("SUPPORT_PHONE", default="+00 000000000"),  # Teléfono de soporte
            'support_email': Setting.get("SUPPORT_EMAIL", default="joe@doe.com"),  # Email de soporte
        })


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'user_profile.html'  # Aquí debes especificar tu plantilla

    # Método para pasar el contexto con la información del usuario logueado
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user  # Añadimos el usuario logueado al contexto
        return context


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


class OrderCreateView(LoginRequiredMixin, View):
    select_item_template = 'order_form.html'

    def get(self, request, category=None):
        search_query = request.GET.get('search', '')  # Obtener el término de búsqueda de la URL
        items, selected_category = self.get_items_by_category(request.GET.get('category', ''), search_query)

        # Paginación
        paginator = Paginator(items, Setting.get("CATALOG_ITEMS_PAGINATION", default=10))
        page = request.GET.get('page', 1)

        try:
            paginated_items = paginator.page(page)
        except PageNotAnInteger:
            paginated_items = paginator.page(1)
        except EmptyPage:
            paginated_items = paginator.page(paginator.num_pages)

        return render(request, self.select_item_template, {
            'order_form': OrderForm(),
            'item_formset': OrderItemFormSet(),
            'categories': Category.objects.all(),
            'items': paginated_items,  # Usar items paginados
            'paginator': paginator,
            'page_obj': paginated_items,
            'is_paginated': paginated_items.has_other_pages(),
        })

    def post(self, request, category=None):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)
        items, selected_category = self.get_items_by_category(request.GET.get('category', ''))
        alternative_slots = []

        if order_form.is_valid() and item_formset.is_valid():
            try:
                # Try to create the order
                order = self.transaction_order(order_form, item_formset)

            except Exception as e:
                # Mostrar opciones para el equipo
                alternative_slots = self.suggest_alternatives(order_form, item_formset)

                if alternative_slots:
                    # Añadir el mensaje de error con las alternativas
                    messages.error(request, f"{e}. Horarios Alternativos:")
                else:
                    messages.error(request, f"{e}. No se encontraron horarios alternativos.")

            else:
                messages.success(request, "La orden se ha creado exitosamente.")
                return redirect('order_detail', order.pk)

        # Si el formulario es inválido o hay excepciones, realizar la paginación nuevamente
        paginator = Paginator(items, Setting.get("CATALOG_ITEMS_PAGINATION", default=10))
        page = request.GET.get('page', 1)

        try:
            paginated_items = paginator.page(page)
        except PageNotAnInteger:
            paginated_items = paginator.page(1)
        except EmptyPage:
            paginated_items = paginator.page(paginator.num_pages)

        return render(request, self.select_item_template, {
            'order_form': order_form,
            'item_formset': item_formset,
            'categories': Category.objects.all(),
            'alternative_slots': alternative_slots,
            'abrir_modal': True,
            'items': paginated_items,  # Usar items paginados
            'paginator': paginator,
            'page_obj': paginated_items,
            'is_paginated': paginated_items.has_other_pages(),
        })

    def get_items_by_category(self, category, search_query=''):
        """
        Obtiene los artículos filtrados por categoría y por término de 
        búsqueda, si se proporcionan.
        """

        if category:
            category_obj = get_object_or_404(Category, name=category)
            items = category_obj.items.all()
        else:
            items = Item.objects.all()

        # Filtrar por el término de búsqueda
        if search_query:
            items = items.filter(name__icontains=search_query)

        return items, category

    def transaction_order(self, order_form, item_formset) -> Order:
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

                    units = item.units_available(order_date, return_date)

                    if quantity > len(units):  # Verificar que hay suficientes unidades
                        raise Exception(f"No hay suficientes unidades de '{item.name}' disponibles")

                    shuffle(units)  # Revolver los elementos de la lista
                    order.units.add(*units[:quantity])  # Agregar la cantidad de unidades especificadas

            if order.units.count() <= 0:
                raise ValueError("La orden no tiene unidades disponibles.")

        return order

    def suggest_alternatives(self, order_form, item_formset):
        """
        Sugiere alternativas de horarios donde TODOS los artículos solicitados
        estén disponibles simultáneamente, dentro del horario de apertura de la tienda.
        """

        opening_time = Setting.get("STORE_OPENING_TIME", default=time(9, 0))  # Hora de apertura
        closing_time = Setting.get("STORE_CLOSING_TIME", default=time(18, 0))  # Hora de cierre
        order_date = order_form.cleaned_data['order_date']
        return_date = order_form.cleaned_data['return_date']

        max_alternatives = 3  # Limitar a 3 alternativas
        alternatives = []

        # Inicializamos un rango de búsqueda en el tiempo original de la orden
        current_start_time = order_date
        duration = return_date - order_date
        time_increment = timedelta(
            minutes=math.ceil(duration.total_seconds() / 60))  # Incremento en minutos según la duración

        # Limitar el tiempo máximo de búsqueda a 24 horas adicionales
        max_search_time = order_date + timedelta(days=1)

        while current_start_time < max_search_time and len(alternatives) < max_alternatives:
            all_items_available = True

            # Verificar si la hora de inicio y fin están dentro del horario de apertura y cierre
            start_time_only = current_start_time.time()
            end_time_only = (current_start_time + duration).time()

            start_in_hours = opening_time <= start_time_only <= closing_time
            end_in_hours = opening_time <= end_time_only <= closing_time

            if not start_in_hours or not end_in_hours:
                current_start_time += time_increment
                continue  # Si el horario no está dentro de los límites, se pasa al siguiente intervalo

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

            # Incrementamos el tiempo de búsqueda según el incremento definido
            current_start_time += time_increment

        return alternatives


class OrderHistoryListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_history_list.html'
    context_object_name = 'orders'

    # agregar esto a una configuración del sistema
    paginate_by = 100

    def get_queryset(self):
        # Incluye las órdenes del usuario que han pasado su fecha o que tienen uno de los estados específicos
        return Order.objects.filter(
            Q(user=self.request.user) &
            (
                Q(order_date__lt=timezone.now()) |  # Órdenes cuyo order_date ha pasado
                Q(status__in=[
                    OrderStatusChoices.CANCELLED,
                    OrderStatusChoices.REJECTED,
                    OrderStatusChoices.RETURNED
                ])  # Órdenes en estos estados
            )
        ).order_by('-order_date')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderAuthorize(LoginRequiredMixin, View):
    """Vista para aprobar (autorizar) una orden solo si está pendiente."""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)

        # Verificar si la orden está pendiente antes de aprobarla
        try:
            order.aprove(request.user)  # Método actualizado en el modelo
            messages.success(request, "La orden ha sido autorizada (aprobada).")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('order_detail', order.pk)


class DeliverOrderView(LoginRequiredMixin, View):
    """Vista para marcar una orden como entregada."""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)

        try:
            order.deliver()  # Método actualizado en el modelo
            messages.success(request, "La orden ha sido marcada como entregada.")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('order_detail', order.pk)


class ReturnOrderView(LoginRequiredMixin, View):
    """Vista para marcar una orden como devuelta."""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)

        try:
            order.return_order()  # Método actualizado en el modelo
            messages.success(request, "La orden ha sido marcada como devuelta.")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('order_detail', order.pk)


class RejectOrderView(LoginRequiredMixin, View):
    """Vista para rechazar una orden."""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)

        try:
            order.reject(request.user)  # Método actualizado en el modelo
            messages.success(request, "La orden ha sido rechazada.")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('order_detail', order.pk)


class CancelOrderView(LoginRequiredMixin, View):
    """Vista para cancelar una orden."""

    def get(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk)

        try:
            order.cancel()  # Método actualizado en el modelo
            messages.success(request, "La orden ha sido cancelada.")
        except ValidationError as e:
            messages.error(request, str(e))

        return redirect('order_detail', order.pk)
