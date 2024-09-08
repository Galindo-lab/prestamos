from random import shuffle

from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


"""
Información de artículos
"""


class Category(models.Model):
    """

    """

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    """

    """

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='items', blank=True)
    
    
    def avalable_units(self):
        return Unit.objects.filter(item=self, available=True)
    
    
    def find_alternative_availability(self, start_date, end_date, max_duration_increase=timedelta(hours=2)):
        """
        Busca horarios alternativos disponibles para el item en incrementos de duración.
        
        :param start_date: Fecha y hora de inicio de la búsqueda
        :param end_date: Fecha y hora de fin de la búsqueda
        :param max_duration_increase: Máximo incremento de la duración permitido
        :return: Primer intervalo disponible como (start_time, end_time) o None si no hay disponibilidad
        """
        duration = end_date - start_date  # Duración original de la orden
        time_increment = timedelta(hours=1)  # Incrementos de búsqueda (en este caso, de 1 hora)
        max_search_time = start_date + timedelta(days=1)  # Búsqueda en las próximas 24 horas

        current_time = start_date

        while current_time < max_search_time:
            # Primero, buscar con la duración original
            available_units = self.units_available(current_time, current_time + duration)
            if available_units:  # Si hay unidades disponibles en ese rango de tiempo
                return current_time, current_time + duration

            # Luego, buscar incrementando la duración, hasta un máximo de 2 horas adicionales
            for increment in range(1, int(max_duration_increase.total_seconds() // 3600) + 1):
                new_duration = duration + timedelta(hours=increment)
                alternative_units = self.units_available(current_time, current_time + new_duration)
                if alternative_units:  # Si hay unidades disponibles con la nueva duración
                    return current_time, current_time + new_duration

            # Avanzar en el tiempo (en incrementos de una hora)
            current_time += time_increment

        # Si no se encuentra ninguna disponibilidad dentro del rango de búsqueda
        return None

    def units_available(self, start_date, end_date):
        """
        Verifica la disponibilidad de unidades del artículo entre las fechas especificadas.
        
        :param start_date: Fecha y hora de inicio
        :param end_date: Fecha y hora de finalización
        :return: Una lista de unidades disponibles
        """
        return [unit for unit in self.units.all() if unit.is_available(start_date, end_date)]

    def __str__(self):
        return self.name


class Unit(models.Model):
    """

    """

    class Meta:
        verbose_name = "Unidad"
        verbose_name_plural = "Unidades"
        unique_together = ('item', 'serial_number')

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='units')
    serial_number = models.CharField(max_length=255)
    available = models.BooleanField(default=True)
    
    def find_alternative_availability(self, start_date, end_date):
        """
        Busca disponibilidad en horas dentro del mismo día.
        :param start_date: Fecha de inicio de la búsqueda
        :param end_date: Fecha final (mismo día)
        :return: La primera hora disponible o None si no hay disponibilidad
        """
        current_time = start_date
        delta = timedelta(hours=1)  # Incremento de una hora para la búsqueda

        while current_time + delta <= end_date:
            available_units = self.units_available(current_time, current_time + delta)
            if available_units:  # Si hay unidades disponibles en esa hora
                return current_time, current_time + delta

            current_time += delta

        # Si no encuentra disponibilidad durante el día
        return None

    def is_available(self, start_date, end_date):
        overlapping_orders = self.orders.filter(models.Q(order_date__lt=end_date, return_date__gt=start_date,
                                                         status__in=[OrderStatusChoices.PENDING,
                                                                     OrderStatusChoices.APPROVED,
                                                                     OrderStatusChoices.DELIVERED]))
        return not overlapping_orders.exists() and self.available

    def __str__(self):
        return f'{self.item.name} - {self.serial_number}'


"""
Ordenes, Reportes y estados
"""


class OrderStatusChoices(models.TextChoices):
    """

    """

    PENDING = 'pending', _('Pendiente')
    CANCELLED = 'cancelled', _('Cancelada')
    APPROVED = 'approved', _('Aprobada')
    REJECTED = 'rejected', _('Rechazada')
    DELIVERED = 'delivered', _('Entregada')
    RETURNED = 'returned', _('Devuelta')


class Order(models.Model):
    """

    """

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Ordenes"
        ordering = ["-created_at"]

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_date = models.DateTimeField(default=timezone.now, null=False)
    return_date = models.DateTimeField(default=timezone.now, null=False)
    units = models.ManyToManyField(Unit, related_name='orders')
    status = models.CharField(max_length=10, choices=OrderStatusChoices.choices, default=OrderStatusChoices.PENDING)
    approved_by = models.ForeignKey(to=User, related_name='approved_orders', null=True, blank=True,
                                    on_delete=models.SET_NULL, default=None)

    def add_item(self, item, quantity):
        """

        :param item:
        :param quantity:
        :return:
        """
        units = item.units_available(self.order_date, self.return_date)

        if quantity > len(units):  # Veríficar que hay suficientes unidades
            raise ValidationError("No hay suficientes unidades de '" + str(item.name) + "' diponibles")

        shuffle(units)  # revolver los elementos de la lista
        self.units.add(*(units[:quantity]))  # agregar la cantidad de unidades especificadas

    def get_report(self):
        """

        :return:
        """
        return getattr(self, 'reports', None)

    def __str__(self):
        return f'Orden {self.id} - {self.user.username}'


class Report(models.Model):
    class Meta:
        verbose_name_plural = "Reportes"

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='reports', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.OneToOneField(to=Order, on_delete=models.CASCADE, related_name='reports')
    details = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
