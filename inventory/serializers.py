from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'quantity', 'price', 'qr_code']
        extra_kwargs = {
            'qr_code': {'required': True},  # ✅ Ensure qr_code is included and writable
        }
