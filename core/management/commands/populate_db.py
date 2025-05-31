from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from core.models import Category, Product, Customer, Order, OrderItem, Inventory, SalesRecord
import random
from datetime import timedelta
import decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database population...')

        self.create_users()
        self.create_categories()
        self.create_products()
        self.create_customers()
        self.create_orders()

        self.stdout.write(self.style.SUCCESS('Database successfully populated!'))

    def create_users(self):
        self.stdout.write('Creating users...')

        # Create admin user if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin'
            )

        # Create manager user
        if not User.objects.filter(username='manager').exists():
            User.objects.create_user(
                username='manager',
                email='manager@example.com',
                password='manager123',
                first_name='Manager',
                last_name='User',
                role='manager'
            )

        # Create staff user
        if not User.objects.filter(username='staff').exists():
            User.objects.create_user(
                username='staff',
                email='staff@example.com',
                password='staff123',
                first_name='Staff',
                last_name='User',
                role='staff'
            )

        self.stdout.write(self.style.SUCCESS('Users created successfully!'))

    def create_categories(self):
        self.stdout.write('Creating product categories...')

        categories = [
            {
                'name': 'T-Shirts',
                'description': 'Casual and comfortable t-shirts for everyday wear'
            },
            {
                'name': 'Jeans',
                'description': 'Durable denim jeans in various styles and fits'
            },
            {
                'name': 'Dresses',
                'description': 'Elegant dresses for various occasions'
            },
            {
                'name': 'Jackets',
                'description': 'Stylish jackets and outerwear for all seasons'
            },
            {
                'name': 'Accessories',
                'description': 'Belts, hats, scarves and other fashion accessories'
            }
        ]

        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )

        self.stdout.write(self.style.SUCCESS('Categories created successfully!'))

    def create_products(self):
        self.stdout.write('Creating products...')

        # Get all categories
        categories = Category.objects.all()

        # Sample product data
        products_data = [
            # T-Shirts
            {
                'name': 'Classic Cotton T-Shirt',
                'description': 'Comfortable 100% cotton t-shirt with a classic fit',
                'price': '19.99',
                'size': 'M',
                'color': 'White',
                'category_name': 'T-Shirts'
            },
            {
                'name': 'Graphic Print T-Shirt',
                'description': 'Bold graphic print t-shirt with a modern design',
                'price': '24.99',
                'size': 'L',
                'color': 'Black',
                'category_name': 'T-Shirts'
            },
            {
                'name': 'V-Neck T-Shirt',
                'description': 'Soft v-neck t-shirt with a slim fit',
                'price': '22.99',
                'size': 'S',
                'color': 'Navy',
                'category_name': 'T-Shirts'
            },

            # Jeans
            {
                'name': 'Slim Fit Jeans',
                'description': 'Modern slim fit jeans with stretch comfort',
                'price': '49.99',
                'size': 'M',
                'color': 'Blue',
                'category_name': 'Jeans'
            },
            {
                'name': 'Relaxed Fit Jeans',
                'description': 'Comfortable relaxed fit jeans for everyday wear',
                'price': '44.99',
                'size': 'L',
                'color': 'Dark Blue',
                'category_name': 'Jeans'
            },
            {
                'name': 'Skinny Jeans',
                'description': 'Trendy skinny jeans with a fashionable look',
                'price': '54.99',
                'size': 'S',
                'color': 'Black',
                'category_name': 'Jeans'
            },

            # Dresses
            {
                'name': 'Summer Floral Dress',
                'description': 'Light and airy floral print dress perfect for summer',
                'price': '39.99',
                'size': 'M',
                'color': 'Floral',
                'category_name': 'Dresses'
            },
            {
                'name': 'Cocktail Dress',
                'description': 'Elegant cocktail dress for special occasions',
                'price': '79.99',
                'size': 'S',
                'color': 'Black',
                'category_name': 'Dresses'
            },
            {
                'name': 'Maxi Dress',
                'description': 'Long flowing maxi dress with a bohemian style',
                'price': '59.99',
                'size': 'L',
                'color': 'Blue',
                'category_name': 'Dresses'
            },

            # Jackets
            {
                'name': 'Denim Jacket',
                'description': 'Classic denim jacket with a vintage wash',
                'price': '69.99',
                'size': 'M',
                'color': 'Blue',
                'category_name': 'Jackets'
            },
            {
                'name': 'Leather Jacket',
                'description': 'Stylish faux leather jacket with a modern cut',
                'price': '89.99',
                'size': 'L',
                'color': 'Black',
                'category_name': 'Jackets'
            },
            {
                'name': 'Windbreaker',
                'description': 'Lightweight windbreaker jacket for outdoor activities',
                'price': '49.99',
                'size': 'S',
                'color': 'Red',
                'category_name': 'Jackets'
            },

            # Accessories
            {
                'name': 'Leather Belt',
                'description': 'Premium quality leather belt with metal buckle',
                'price': '29.99',
                'size': 'M',
                'color': 'Brown',
                'category_name': 'Accessories'
            },
            {
                'name': 'Winter Scarf',
                'description': 'Warm knitted scarf for cold weather',
                'price': '19.99',
                'size': 'ONE',
                'color': 'Gray',
                'category_name': 'Accessories'
            },
            {
                'name': 'Baseball Cap',
                'description': 'Casual baseball cap with embroidered logo',
                'price': '24.99',
                'size': 'ONE',
                'color': 'Navy',
                'category_name': 'Accessories'
            }
        ]

        for product_data in products_data:
            category = Category.objects.get(name=product_data['category_name'])

            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'price': decimal.Decimal(product_data['price']),
                    'size': product_data['size'],
                    'color': product_data['color'],
                    'category': category
                }
            )

            # Create or update inventory for this product
            if created:
                quantity = random.randint(10, 100)
                restock_level = random.randint(5, 20)

                Inventory.objects.create(
                    product=product,
                    quantity=quantity,
                    restock_level=restock_level,
                    last_restock_date=timezone.now() - timedelta(days=random.randint(1, 30)),
                    next_restock_date=timezone.now() + timedelta(days=random.randint(1, 30)) if random.choice(
                        [True, False]) else None
                )

        self.stdout.write(self.style.SUCCESS('Products created successfully!'))

    def create_customers(self):
        self.stdout.write('Creating customers...')

        customers_data = [
            {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'phone': '555-123-4567',
                'address': '123 Main St, Anytown, USA'
            },
            {
                'name': 'Sarah Johnson',
                'email': 'sarah.j@example.com',
                'phone': '555-234-5678',
                'address': '456 Oak Ave, Somewhere, USA'
            },
            {
                'name': 'Michael Brown',
                'email': 'mbrown@example.com',
                'phone': '555-345-6789',
                'address': '789 Pine Rd, Nowhere, USA'
            },
            {
                'name': 'Emily Davis',
                'email': 'emily.davis@example.com',
                'phone': '555-456-7890',
                'address': '101 Elm St, Anyplace, USA'
            },
            {
                'name': 'David Wilson',
                'email': 'dwilson@example.com',
                'phone': '555-567-8901',
                'address': '202 Maple Dr, Somewhere, USA'
            },
            {
                'name': 'Jennifer Taylor',
                'email': 'jtaylor@example.com',
                'phone': '555-678-9012',
                'address': '303 Cedar Ln, Anytown, USA'
            },
            {
                'name': 'Robert Martinez',
                'email': 'rmartinez@example.com',
                'phone': '555-789-0123',
                'address': '404 Birch Blvd, Nowhere, USA'
            },
            {
                'name': 'Lisa Anderson',
                'email': 'landerson@example.com',
                'phone': '555-890-1234',
                'address': '505 Walnut St, Anyplace, USA'
            },
            {
                'name': 'James Thomas',
                'email': 'jthomas@example.com',
                'phone': '555-901-2345',
                'address': '606 Spruce Ave, Somewhere, USA'
            },
            {
                'name': 'Patricia White',
                'email': 'pwhite@example.com',
                'phone': '555-012-3456',
                'address': '707 Fir Rd, Anytown, USA'
            }
        ]

        for customer_data in customers_data:
            Customer.objects.get_or_create(
                name=customer_data['name'],
                defaults={
                    'email': customer_data['email'],
                    'phone': customer_data['phone'],
                    'address': customer_data['address']
                }
            )

        self.stdout.write(self.style.SUCCESS('Customers created successfully!'))

    def create_orders(self):
        self.stdout.write('Creating orders...')

        customers = Customer.objects.all()
        products = Product.objects.all()

        # Generate orders for the past 30 days
        for day in range(30, 0, -1):
            order_date = timezone.now() - timedelta(days=day)

            # Create 1-3 orders per day
            for _ in range(random.randint(1, 3)):
                customer = random.choice(customers)
                status_choices = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
                status_weights = [0.1, 0.2, 0.3, 0.3, 0.1]  # Probability weights
                status = random.choices(status_choices, weights=status_weights, k=1)[0]

                with transaction.atomic():
                    order = Order.objects.create(
                        customer=customer,
                        order_date=order_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59)),
                        status=status,
                        notes=random.choice(['', 'Please deliver ASAP', 'Gift wrap requested',
                                             'Call before delivery']) if random.random() < 0.3 else ''
                    )

                    # Generate a random order number
                    order.order_number = f"ORD-{order.id:06d}"
                    order.save()

                    # Add 1-5 items to the order
                    total_amount = decimal.Decimal('0.00')
                    for _ in range(random.randint(1, 5)):
                        product = random.choice(products)
                        quantity = random.randint(1, 3)
                        price = product.price

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=price
                        )

                        total_amount += price * quantity

                        # Update inventory
                        inventory = Inventory.objects.get(product=product)
                        if inventory.quantity >= quantity:
                            inventory.quantity -= quantity
                            inventory.save()

                    # Update order total
                    order.total_amount = total_amount
                    order.save()

        self.stdout.write(self.style.SUCCESS('Orders created successfully!'))