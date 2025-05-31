from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum

from .models import Order, OrderItem, SalesRecord


@receiver(post_save, sender=Order)
def update_sales_record(sender, instance, created, **kwargs):
    """Update or create sales record when an order is saved"""
    date = instance.order_date.date()

    # Get all orders for this date
    daily_orders = Order.objects.filter(order_date__date=date)
    total_sales = daily_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = daily_orders.count()

    # Update or create the sales record
    SalesRecord.objects.update_or_create(
        date=date,
        defaults={
            'total_sales': total_sales,
            'total_orders': total_orders
        }
    )


@receiver(post_delete, sender=Order)
def update_sales_record_on_delete(sender, instance, **kwargs):
    """Update sales record when an order is deleted"""
    date = instance.order_date.date()

    # Get all remaining orders for this date
    daily_orders = Order.objects.filter(order_date__date=date)
    total_sales = daily_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = daily_orders.count()

    # Update the sales record
    SalesRecord.objects.update_or_create(
        date=date,
        defaults={
            'total_sales': total_sales,
            'total_orders': total_orders
        }
    )