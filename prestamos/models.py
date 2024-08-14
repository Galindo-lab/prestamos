from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

"""
Información de artículos
"""


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categorías"

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    class Meta:
        verbose_name_plural = "Artículo"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='items')

    def units_available(self, start_date, end_date):
        return [item for item in Unit.objects.filter(item=self) if item.is_available(start_date, end_date)]

    def __str__(self):
        return self.name


class Unit(models.Model):
    class Meta:
        verbose_name_plural = "Unidades"

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='units')
    serial_number = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)

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
    PENDING = 'pending', _('Pendiente')
    CANCELLED = 'cancelled', _('Cancelada')
    APPROVED = 'approved', _('Aprobada')
    REJECTED = 'rejected', _('Rechazada')
    DELIVERED = 'delivered', _('Entregada')
    RETURNED = 'returned', _('Devuelta')


class Order(models.Model):
    class Meta:
        verbose_name_plural = "Ordenes"

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now, null=False)
    return_date = models.DateTimeField(default=timezone.now, null=False)
    units = models.ManyToManyField(Unit, related_name='orders')
    status = models.CharField(max_length=10, choices=OrderStatusChoices.choices, default=OrderStatusChoices.PENDING)
    approved_by = models.ForeignKey(to=User, related_name='approved_orders', null=True, blank=True,
                                    on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return f'Orden {self.id} - {self.user.username}'


class Report(models.Model):
    class Meta:
        verbose_name_plural = "Reportes"

    user = models.ForeignKey(to=User, on_delete=models.SET_NULL, related_name='reports', null=True)
    order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='reports')
    active = models.BooleanField(default=True)
    details = models.TextField(blank=True, null=True)
