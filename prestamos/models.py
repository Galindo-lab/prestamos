from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

"""
Información de artículos
"""


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categorías"


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='items')

    def units_available(self, start_date, end_date):
        return [item for item in Unit.objects.filter(item=self) if item.is_available(start_date, end_date)]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Artículo"


class Unit(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='units')
    serial_number = models.CharField(max_length=255, unique=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.item.name} - {self.serial_number}'

    def is_available(self, start_date, end_date):
        overlapping_orders = self.orders \
            .filter(models.Q(order_date__lt=end_date, return_date__gt=start_date, canceled=False))
        return not overlapping_orders.exists() and self.available

    class Meta:
        verbose_name_plural = "Unidades"


"""
Ordenes y estados
"""


class OrderStatusChoices(models.TextChoices):
    PENDING = 'pending', _('Pending')
    APPROVED = 'approved', _('Approved')
    REJECTED = 'rejected', _('Rejected')


class Order(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    canceled = models.BooleanField(default=False)
    order_date = models.DateTimeField(default=timezone.now, null=False)
    return_date = models.DateTimeField(default=timezone.now, null=False)
    units = models.ManyToManyField(Unit, related_name='orders')
    status = models.CharField(max_length=10, choices=OrderStatusChoices.choices, default='pending')
    approved_by = models.ForeignKey(to=User, related_name='approved_orders', null=True, blank=True,
                                    on_delete=models.SET_NULL, default=None)

    def __str__(self):
        return f'Orden {self.id} - {self.user.username}'

    class Meta:
        verbose_name_plural = "Ordenes"
