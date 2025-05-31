from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import logout
from django.shortcuts import redirect
import csv
import json
from datetime import datetime, timedelta

from .models import User, Product, Category, Customer, Order, OrderItem, Inventory, SalesRecord
from .forms import (
    CustomAuthenticationForm, UserForm, ProductForm, CategoryForm,
    CustomerForm, OrderForm, OrderItemFormSet, InventoryForm
)

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('profile')

# Helper functions for permissions
def is_admin(user):
    return user.role == User.ADMIN


def is_manager_or_admin(user):
    return user.role in [User.ADMIN, User.MANAGER]


# Authentication views
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'core/login.html'


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserForm(instance=request.user)

    return render(request, 'core/profile.html', {'form': form})


# Dashboard view
@login_required
def dashboard(request):
    # Get sales data for today
    today = timezone.now().date()
    today_sales = Order.objects.filter(order_date__date=today).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )

    # Get yesterday's data for comparison
    yesterday = today - timedelta(days=1)
    yesterday_sales = Order.objects.filter(order_date__date=yesterday).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )

    # Calculate percentage changes
    total_sales_change = 0
    if yesterday_sales['total'] and today_sales['total']:
        total_sales_change = ((today_sales['total'] - yesterday_sales['total']) / yesterday_sales['total']) * 100

    total_orders_change = 0
    if yesterday_sales['count'] and today_sales['count']:
        total_orders_change = ((today_sales['count'] - yesterday_sales['count']) / yesterday_sales['count']) * 100

    # Get top products
    top_products = OrderItem.objects.values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:5]

    # Get low stock items
    low_stock_items = Inventory.objects.filter(
        quantity__lte=F('restock_level')
    ).select_related('product')[:5]

    # Get recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-order_date')[:5]

    # Get customer count
    customer_count = Customer.objects.count()
    new_customers_today = Customer.objects.filter(created_at__date=today).count()

    # Get product count
    product_count = Product.objects.count()

    context = {
        'total_sales': today_sales['total'] or 0,
        'total_sales_change': total_sales_change,
        'total_orders': today_sales['count'] or 0,
        'total_orders_change': total_orders_change,
        'top_products': top_products,
        'low_stock_items': low_stock_items,
        'recent_orders': recent_orders,
        'customer_count': customer_count,
        'new_customers_today': new_customers_today,
        'product_count': product_count,
    }

    return render(request, 'core/dashboard.html', context)

# Product views
@login_required
def product_list(request):
    products = Product.objects.select_related('category').all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/product_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
@user_passes_test(is_manager_or_admin)
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            # Create inventory record
            Inventory.objects.create(product=product)
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        inventory = product.inventory
    except Inventory.DoesNotExist:
        inventory = Inventory.objects.create(product=product)

    return render(request, 'core/product_detail.html', {'product': product, 'inventory': inventory})


@login_required
@user_passes_test(is_manager_or_admin)
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})


@login_required
@user_passes_test(is_admin)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')

    return render(request, 'core/confirm_delete.html', {'object': product, 'object_name': 'Product'})


# Category views
@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})


@login_required
@user_passes_test(is_manager_or_admin)
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'core/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
@user_passes_test(is_manager_or_admin)
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'core/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')

    return render(request, 'core/confirm_delete.html', {'object': category, 'object_name': 'Category'})


# Customer views
@login_required
def customer_list(request):
    customers = Customer.objects.all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/customer_list.html', {'page_obj': page_obj, 'search_query': search_query})


@login_required
@user_passes_test(is_manager_or_admin)
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully!')
            return redirect('customer_list')
    else:
        form = CustomerForm()

    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.all().order_by('-order_date')

    return render(request, 'core/customer_detail.html', {'customer': customer, 'orders': orders})


@login_required
@user_passes_test(is_manager_or_admin)
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)

    return render(request, 'core/customer_form.html', {'form': form, 'title': 'Edit Customer'})


@login_required
@user_passes_test(is_admin)
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully!')
        return redirect('customer_list')

    return render(request, 'core/confirm_delete.html', {'object': customer, 'object_name': 'Customer'})


# Order views
@login_required
def order_list(request):
    orders = Order.objects.select_related('customer').all()

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_number__icontains=search_query) |
            Q(customer__name__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/order_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES
    })


@login_required
@user_passes_test(is_manager_or_admin)
def order_add(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()

            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()

                # Calculate total amount
                total = sum(item.quantity * item.price for item in order.items.all())
                order.total_amount = total
                order.save()

                # Update inventory
                for item in order.items.all():
                    inventory = item.product.inventory
                    inventory.quantity = max(0, inventory.quantity - item.quantity)
                    inventory.save()

                messages.success(request, 'Order created successfully!')
                return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'core/order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Order'
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = order.items.select_related('product').all()

    return render(request, 'core/order_detail.html', {'order': order, 'items': items})


@login_required
@user_passes_test(is_manager_or_admin)
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()

            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()

                # Recalculate total amount
                total = sum(item.quantity * item.price for item in order.items.all())
                order.total_amount = total
                order.save()

                messages.success(request, 'Order updated successfully!')
                return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'core/order_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Order'
    })


@login_required
@user_passes_test(is_admin)
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Order deleted successfully!')
        return redirect('order_list')

    return render(request, 'core/confirm_delete.html', {'object': order, 'object_name': 'Order'})


# Inventory views
@login_required
def inventory_list(request):
    inventory_items = Inventory.objects.select_related('product').all()

    # Filter by stock status
    stock_filter = request.GET.get('stock', '')
    if stock_filter == 'low':
        inventory_items = inventory_items.filter(quantity__lte=F('restock_level'))

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        inventory_items = inventory_items.filter(product__name__icontains=search_query)

    # Pagination
    paginator = Paginator(inventory_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'core/inventory_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'stock_filter': stock_filter
    })


@login_required
@user_passes_test(is_manager_or_admin)
def inventory_edit(request, pk):
    inventory = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory updated successfully!')
            return redirect('inventory_list')
    else:
        form = InventoryForm(instance=inventory)

    return render(request, 'core/inventory_form.html', {
        'form': form,
        'product': inventory.product,
        'title': 'Update Inventory'
    })


# API endpoints for charts
@login_required
def sales_data(request):
    # Get sales data for the last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    sales_data = []
    current_date = start_date

    while current_date <= end_date:
        daily_sales = Order.objects.filter(order_date__date=current_date).aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        sales_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'amount': float(daily_sales)
        })

        current_date += timedelta(days=1)

    return JsonResponse(sales_data, safe=False)


@login_required
def inventory_data(request):
    # Get inventory data for visualization
    inventory_data = Inventory.objects.select_related('product').values(
        'product__name', 'quantity', 'restock_level'
    )

    return JsonResponse(list(inventory_data), safe=False)


@login_required
def top_products(request):
    # Get top selling products
    period = request.GET.get('period', '30')  # Default to 30 days
    days = int(period)

    start_date = timezone.now() - timedelta(days=days)

    top_products = OrderItem.objects.filter(
        order__order_date__gte=start_date
    ).values(
        'product__name'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:10]

    return JsonResponse(list(top_products), safe=False)


# Export functionality
@login_required
@user_passes_test(is_manager_or_admin)
def export_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Category', 'Price', 'Size', 'Color', 'Stock'])

    products = Product.objects.select_related('category', 'inventory').all()

    for product in products:
        try:
            stock = product.inventory.quantity
        except Inventory.DoesNotExist:
            stock = 0

        writer.writerow([
            product.name,
            product.category.name,
            product.price,
            product.size,
            product.color,
            stock
        ])

    return response


@login_required
@user_passes_test(is_manager_or_admin)
def export_customers(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Address', 'Created At'])

    customers = Customer.objects.all()

    for customer in customers:
        writer.writerow([
            customer.name,
            customer.phone,
            customer.email,
            customer.address,
            customer.created_at.strftime('%Y-%m-%d')
        ])

    return response


@login_required
@user_passes_test(is_manager_or_admin)
def export_orders(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Customer', 'Date', 'Status', 'Total Amount'])

    orders = Order.objects.select_related('customer').all()

    for order in orders:
        writer.writerow([
            order.order_number,
            order.customer.name,
            order.order_date.strftime('%Y-%m-%d %H:%M'),
            order.get_status_display(),
            order.total_amount
        ])

    return response