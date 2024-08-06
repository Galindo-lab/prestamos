from django.contrib import admin

from .models import Category, Item, Unit, Order

class CategoryItemInline(admin.TabularInline):
    model = Item.category.through
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [CategoryItemInline]  # Añadir el TabularInline aquí

class UnitInlineForItem(admin.TabularInline):
    model = Unit
    extra = 1


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', )
    list_filter = ('category',)
    filter_horizontal = ('category',)
    inlines = [UnitInlineForItem]


class UnitAdmin(admin.ModelAdmin):
    list_display = ('item', 'serial_number')
    search_fields = ('serial_number', 'item__name')
    list_filter = ('item',)


class UnitInlineForOrder(admin.TabularInline):
    model = Order.units.through  # Through table for the many-to-many relationship
    autocomplete_fields = ['unit']
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'return_date')
    search_fields = ('user__username', 'user__email')
    list_filter = ('order_date', 'return_date')
    exclude = ('units',)
    autocomplete_fields = ['user']
    inlines = [UnitInlineForOrder]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Order, OrderAdmin)
