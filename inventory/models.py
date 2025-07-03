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
    ACTION_CHOICES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('update', 'Updated'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
