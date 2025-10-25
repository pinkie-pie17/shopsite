from django.contrib import admin
from .models import Item, CartItem, Order, OrderItem

# Register your models here.


admin.site.register(Item)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)