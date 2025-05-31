from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Product, Category, Customer, Order, OrderItem, Inventory

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Bootstrap styling"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class UserForm(forms.ModelForm):
    """Form for user profile"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'profile_image']
        widgets = {
            'profile_image': forms.FileInput(),
        }

class CategoryForm(forms.ModelForm):
    """Form for product categories"""
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    """Form for product creation and editing"""
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'size', 'color', 'description', 'image']
        widgets = {
            'image': forms.FileInput(),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InventoryForm(forms.ModelForm):
    """Form for inventory management"""
    class Meta:
        model = Inventory
        fields = ['quantity', 'restock_level', 'next_restock_date']
        widgets = {
            'next_restock_date': forms.DateInput(attrs={'type': 'date'}),
        }

class CustomerForm(forms.ModelForm):
    """Form for customer creation and editing"""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    """Form for order creation and editing"""
    class Meta:
        model = Order
        fields = ['customer', 'status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class OrderItemForm(forms.ModelForm):
    """Form for order items"""
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

OrderItemFormSet = forms.inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True
)