# views.py
from random import shuffle

from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import OrderForm, AuthorizeForm, OrderItemFormSet
from .models import Order


class OrderAuthorize(UpdateView):
    model = Order
    form_class = AuthorizeForm
    template_name = 'order_authorize.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.approved_by = self.request.user
        return super().form_valid(form)


class OrderCreateView(View):
    template = 'order_form.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template, {
            'order_form': OrderForm(),
            'item_formset': OrderItemFormSet()
        })

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and item_formset.is_valid():
            try:
                with transaction.atomic():

                    order = order_form.save(commit=False)
                    order.user = request.user
                    order.save()

                    for item_form in item_formset:
                        # agregar unidades a la orden
                        item, quantity = item_form.cleaned_data['item'], item_form.cleaned_data['quantity']
                        units = item.units_available(order.order_date, order.return_date)

                        if quantity > len(units):
                            # verificar que hay suficientes unidades
                            raise Exception("No hay suficientes unidades de '" + str(item.name) + "' diponibles")

                        shuffle(units)  # revolver los elementos de la lista
                        order.units.add(*(units[:quantity]))  # agregar la cantidad de unidades especificadas

            except Exception as e:
                messages.error(request, e)

            else:
                # redirigir a la pagina de detalles de la orden
                messages.success(request, "La orden se ha creado exitosamente.")
                return redirect('order_detail', order.pk)

        return render(request, self.template, {
            'order_form': order_form,
            'item_formset': item_formset
        })


class OrderListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
