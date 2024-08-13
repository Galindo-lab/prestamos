# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory

from .models import Order, Item


class AproveForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['approved_by', 'status']


class OrderItemForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.all())
    quantity = forms.IntegerField(min_value=0)
    def clean(self):
       cleaned_data = super().clean()
       order_date = cleaned_data.get('order_date')
       return_date = cleaned_data.get('return_date')

       if order_date and return_date and order_date >= return_date:
           raise ValidationError('La fecha de inicio de la orden debe ser anterior a la fecha de finalización.')

       return cleaned_data



# cantidad maxima de articulos por solicitud
OrderItemFormSet = formset_factory(OrderItemForm)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_date', 'return_date']
        widgets = {
            'order_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'return_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
        }

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
