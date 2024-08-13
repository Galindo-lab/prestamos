# views.py
from random import random, shuffle

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import OrderForm, AproveForm, OrderItemFormSet
from .models import Order, OrderStatusChoices, Unit


class OrderAprove(UpdateView):
    model = Order
    form_class = AproveForm
    template_name = 'order_form.html'
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        form.instance.status = OrderStatusChoices.APPROVED
        form.instance.approved_by = self.request.user
        return super().form_valid(form)


class OrderCreateView(View):
    def get(self, request, *args, **kwargs):
        order_form = OrderForm()
        item_formset = OrderItemFormSet()
        return render(request, 'order_form.html', {'order_form': order_form, 'item_formset': item_formset})

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(request.POST)
        item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and item_formset.is_valid():
            order = order_form.save(commit=False)
            order.user = request.user
            order.save()

            for item_form in item_formset:
                item, quantity = item_form.cleaned_data['item'], item_form.cleaned_data['quantity']
                units = item.units_available(order.order_date, order.return_date)

                shuffle(units)  # revolver los elementos de la lista

                if quantity > len(units):
                    print("No hay suficientes unidades")
                    render(request, 'order_form.html', {'order_form': order_form, 'item_formset': item_formset})

                order.units.add(*(units[:quantity]))

        return render(request, 'order_form.html', {'order_form': order_form, 'item_formset': item_formset})


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
