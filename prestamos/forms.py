# forms.py
from django import forms
from django.core.exceptions import ValidationError
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
        widget=forms.TextInput()
    )
    quantity = forms.IntegerField(min_value=0)


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

        if order_date and return_date and order_date >= return_date:
            raise ValidationError('La fecha de inicio de la orden debe ser anterior a la fecha de finalización.')

        return cleaned_data

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['order_date', 'return_date', 'units']
#         widgets = {
#             'order_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'return_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#             'units': forms.CheckboxSelectMultiple(),
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         order_date = cleaned_data.get('order_date')
#         return_date = cleaned_data.get('return_date')
#         units = cleaned_data.get('units')
#
#         if order_date and return_date and order_date >= return_date:
#             raise ValidationError('La fecha de inicio de la orden debe ser anterior a la fecha de finalización.')
#
#         if order_date and return_date and units:
#             for unit in units:
#                 if not unit.is_available(order_date, return_date):
#                     raise ValidationError(f'La unidad "{unit}" no está disponible en el rango de fechas especificado.')
#
#         return cleaned_data
