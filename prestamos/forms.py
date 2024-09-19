import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.utils import timezone
from extra_settings.models import Setting

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


"""    def clean(self):
        cleaned_data = super().clean()
        item = cleaned_data.get('item')
        quantity = cleaned_data.get('quantity')
        order_date = self.initial.get('order_date')
        return_date = self.initial.get('return_date')
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

        self.validate_no_past_dates(order_date, return_date)
        self.validate_dates_sequence(order_date, return_date)
        self.validate_open_days(order_date, return_date)
        self.validate_store_hours(order_date, return_date)

        return cleaned_data

    def validate_dates_sequence(self, order_date, return_date):
        """Valida que la fecha de entrega sea anterior a la de devolución"""
        if order_date and return_date and order_date >= return_date:
            raise ValidationError('La fecha de entrega debe ser anterior a la fecha de devolución.')

    def validate_store_hours(self, order_date, return_date):
        """Valida que las horas de las fechas estén dentro del horario de apertura y cierre de la tienda"""
        opening_time = Setting.get("STORE_OPENING_TIME", default=datetime.time(1, 0))
        closing_time = Setting.get("STORE_CLOSING_TIME", default=datetime.time(0, 0))

        opening_time_12hr = opening_time.strftime("%I:%M %p")
        closing_time_12hr = closing_time.strftime("%I:%M %p")

        if order_date.time() < opening_time or return_date.time() < opening_time:
            raise ValidationError(f'Lo más temprano que puede ordenar es {opening_time_12hr}')
        if order_date.time() > closing_time or return_date.time() > closing_time:
            raise ValidationError(f'Lo más tarde que puede ordenar es {closing_time_12hr}')

    def validate_open_days(self, order_date, return_date):
        """Valida que las fechas caigan en días en los que la tienda está abierta"""
        # Obtener los días de apertura y convertir todo a minúsculas
        store_open_days = Setting.get("STORE_OPEN_DAYS", "")
        store_open_days_list = [day.strip().lower() for day in
                                store_open_days.split(",")]  # Elimina espacios y convierte a minúsculas

        # Validar días de apertura
        if order_date:
            order_day = order_date.strftime("%A").lower()  # Obtener el día de la semana en inglés (minúscula)
            if order_day not in store_open_days_list:
                raise ValidationError(f'La tienda no está abierta el día {self.translate_day_to_spanish(order_day)}.')

        if return_date:
            return_day = return_date.strftime("%A").lower()  # Obtener el día de la semana en inglés (minúscula)
            if return_day not in store_open_days_list:
                raise ValidationError(f'La tienda no está abierta el día {self.translate_day_to_spanish(return_day)}.')

    def validate_no_past_dates(self, order_date, return_date):
        """Valida que las fechas no estén en el pasado"""
        now = timezone.now()  # Obtener la fecha y hora actuales

        if order_date and order_date < now:
            raise ValidationError('No se puede hacer un pedido en el pasado.')

        if return_date and return_date < now:
            raise ValidationError('La fecha de devolución no puede estar en el pasado.')

    def translate_day_to_spanish(self, day_in_english):
        """Traduce el nombre del día de la semana del inglés al español solo para los mensajes de error"""
        days_mapping = {
            'monday': 'lunes',
            'tuesday': 'martes',
            'wednesday': 'miércoles',
            'thursday': 'jueves',
            'friday': 'viernes',
            'saturday': 'sábado',
            'sunday': 'domingo'
        }
        return days_mapping.get(day_in_english,
                                day_in_english).capitalize()  # Capitaliza la primera letra para el mensaje
