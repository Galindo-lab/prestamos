# forms.py
from datetime import time

from django import forms
from django.core.exceptions import ValidationError
from extra_settings.models import Setting
from django.forms import formset_factory

from .models import Order, Item, Report



"""
Formulario para aprobar una orden
"""


class AuthorizeForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.RadioSelect,  # Cambiar a botones de radio
        }


"""
Formulario de artículos y unidades
"""


class OrderItemForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        widget=forms.Select()
    )
    quantity = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        order_date = self.initial.get('order_date')
        return_date = self.initial.get('return_date')

        if item and quantity:
            # Verificar si el artículo tiene suficientes unidades disponibles
            available_units = item.avalable_units()
            if len(available_units) < quantity:
                raise ValidationError(f"Solo existen {len(available_units)} unidad(es) del artículo '{item.name}'")

        return cleaned_data

# cantidad maxima de artículos por solicitud
OrderItemFormSet = formset_factory(OrderItemForm, max_num=50, validate_max=True)

"""
Formulario de Reporte
"""


class ReporteForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['details', 'active']


"""
Formulario de Orden
"""


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_date', 'return_date']
        widgets = {
            'order_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'return_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

    def clean(self):
        cleaned_data = super().clean()
        order_date = cleaned_data.get('order_date')
        return_date = cleaned_data.get('return_date')

        opening_time = Setting.get("STORE_OPENING_TIME", default=time(1, 0))
        closing_time = Setting.get("STORE_CLOSING_TIME", default=time(00, 00))

        # Convertimos las horas a formato de 12 horas con AM/PM solo para los mensajes de error
        opening_time_12hr = opening_time.strftime("%I:%M %p")
        closing_time_12hr = closing_time.strftime("%I:%M %p")

        if order_date.time() < opening_time or return_date.time() < opening_time:
            raise ValidationError(f'Lo más temprano que puede ordenar es {opening_time_12hr}')

        if order_date.time() > closing_time or return_date.time() > closing_time:
            raise ValidationError(f'Lo más tarde que puede ordenar es {closing_time_12hr}')

        if order_date and return_date and order_date >= return_date:
            raise ValidationError('La fecha de entrega debe ser anterior a la fecha de devolución.')

        return cleaned_data
