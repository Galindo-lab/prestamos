from django.contrib import admin

from .models import Category, Item, Unit, Order

"""
Categoría y lista de artículos 
"""


class CategoryItemInline(admin.TabularInline):
    model = Item.category.through
    autocomplete_fields = ['item']
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [CategoryItemInline]  # Añadir el TabularInline aquí


"""
Artículos y lista de unidades
"""


class UnitInlineForItem(admin.TabularInline):
    model = Unit
    extra = 0


class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    list_filter = ('category',)
    filter_horizontal = ('category',)
    inlines = [UnitInlineForItem]


"""
Unidades de un artículo
"""


class UnitAdmin(admin.ModelAdmin):
    list_display = ('item', 'serial_number', 'available')
    search_fields = ('serial_number', 'item__name')
    list_filter = ('item',)


"""
Ordenes de un articulo
"""

class UnitInlineForOrder(admin.TabularInline):
    model = Order.units.through  # Through table for the many-to-many relationship
    autocomplete_fields = ['unit']
    extra = 0



class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'return_date', 'approved_by')
    search_fields = ('user__username', 'user__email')
    list_filter = ('order_date', 'return_date')
    exclude = ('units',)
    autocomplete_fields = ['user']
    inlines = [UnitInlineForOrder]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Order, OrderAdmin)
