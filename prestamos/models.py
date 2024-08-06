from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ManyToManyField(Category, related_name='items')

    def __str__(self):
        return self.name


class Unit(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='units')
    serial_number = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.item.name} - {self.serial_number}'

    def is_available(self, start_date, end_date):
        overlapping_orders = self.orders.filter(
            models.Q(order_date__lt=end_date, return_date__gt=start_date)
        )
        return not overlapping_orders.exists()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(blank=True, null=True)
    units = models.ManyToManyField(Unit, related_name='orders')

    def __str__(self):
        return f'Order {self.id} - {self.user.username}'
