from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Customer, Order, OrderItem, Inventory, SalesRecord

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'profile_image')}),
    )

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('order_number', 'customer__name')
    inlines = [OrderItemInline]

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'size', 'color')
    list_filter = ('category', 'size', 'color')
    search_fields = ('name', 'description')

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'restock_level', 'needs_restock', 'last_restock_date')
    list_filter = ('last_restock_date',)
    search_fields = ('product__name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Customer)
admin.site.register(Order, OrderAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(SalesRecord)