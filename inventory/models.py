from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    quantity = models.IntegerField()
    max_capacity = models.IntegerField(default=100)  # New field
    qr_code = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    change_type = models.CharField(
    max_length=10,
    choices=[('in', 'Stock In'), ('out', 'Stock Out')],
    default='in'  # ✅ Default for existing rows during migration
)
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.change_type} - {self.quantity_changed}"
