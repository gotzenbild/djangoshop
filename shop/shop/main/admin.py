from django.contrib import admin
from main.models import Category , Product , Cart, CartItem, Order, Phone , MainLogo
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Phone)
admin.site.register(MainLogo)