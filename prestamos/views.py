# views.py
from random import shuffle

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import OrderForm, AuthorizeForm, OrderItemFormSet, ReporteForm
from .models import Order, Report, Item


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
    template = 'order_form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template, {
            'order_form': OrderForm(),
            'item_formset': OrderItemFormSet(),
            'items': Item.objects.all()
        })

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():

                    order_form.instance.user = self.request.user
                    order = order_form.save()

                    for item_form in item_formset:
                        # agregar unidades a la orden
                        item, quantity = item_form.cleaned_data['item'], item_form.cleaned_data['quantity']

                        # TODO: extraer esto y convertirlo en un método para orden
                        # -----
                        if quantity < 0:
                            # si solicito 0 unidades del articulo ignorar
                            continue

                        units = item.units_available(order.order_date, order.return_date)

                        if quantity > len(units):
                            # Veríficar que hay suficientes unidades
                            raise Exception("No hay suficientes unidades de '" + str(item.name) + "' diponibles")

                        shuffle(units)  # revolver los elementos de la lista
                        order.units.add(*(units[:quantity]))  # agregar la cantidad de unidades especificadas
                        # -----

                    if order.units.count() <= 0:
                        raise Exception("La orden no tiene unidades")


            except Exception as e:
                messages.error(request, e)

            else:
                # redirigir a la pagina de detalles de la orden
                messages.success(request, "La orden se ha creado exitosamente.")
                return redirect('order_detail', order.pk)

        return render(request, self.template, {
            'order_form': order_form,
            'item_formset': item_formset,
            'items': Item.objects.all()
        })


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
