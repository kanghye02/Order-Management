from django.db import models
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)

    def get_user_orders(self): #trả về các đơn hàng của người dùng cụ thể
        return self.order_set.all()

class Category(models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, help_text=_("Parent category of this category (if any)."))

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='product_images/', default='homepage/image404.png', null=True, blank=True, help_text=_("Product image"))
    description = models.CharField(max_length=255, help_text=_("Brief description of the product."))
    base_price = models.DecimalField(max_digits=12, decimal_places=0, help_text=_("The origin price of the product."))
    number_in_stock = models.IntegerField(default=0, help_text=_("Quantity of the product available in stock."))
    sold_number = models.IntegerField(default=0, help_text=_("Number of products sold."))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    def is_available(self):
        return self.number_in_stock > 0

    def get_stock_count(self):
        return self.number_in_stock
    
    class Meta:
        ordering = ['name']

        def __str__(self):
            return self.name

class Order(models.Model):
    order_date = models.DateTimeField(default=timezone.now, help_text=_("Date of the order."))
    ORDER_STATUS = (
        (0, 'Pending'),
        (1, 'Ongoing'),
        (2, 'Cancelled'),
        (3, 'Rejected'),
        (4, 'Completed'),
    )
    status = models.IntegerField(choices=ORDER_STATUS, default=0, help_text=_("Status of the order."))
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    order_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text=_("total cost of order."))

class OrderDetail(models.Model):
    price = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text=_("Price of product at order."))
    quantity = models.IntegerField(default=0, help_text=_("total quantity of products ordered."))
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, help_text=_("total cost of order."))

class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

class CartItem(models.Model):
    quantity = models.IntegerField(default=1, help_text=_("Quantity of each product in the cart."))
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class BestSeller(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sold_number = models.IntegerField(default=0, help_text=_("The number of sales of the best-selling product."))

    class Meta:
        verbose_name = _("Best Seller")
        verbose_name_plural = _("Best Sellers")

class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, help_text=_("Brief description of the promotion."))
    dis_percent = models.IntegerField(default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)

class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
