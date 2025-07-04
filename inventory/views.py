import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Product, StockHistory
from .serializers import StockHistorySerializer, ProductSerializer
from django.http import JsonResponse
from django.core.management import call_command
from django.db import models

User = get_user_model()

# -----------------------
# ✅ Product Views
# -----------------------

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def list_products(request):
    try:
        if request.method == 'GET':
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                product = serializer.save()

                # ✅ Log initial stock
                StockHistory.objects.create(
                    product=product,
                    change_type='in',
                    quantity_changed=product.quantity
                )

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_by_qr(request, qr_code):
    print(f"Received QR code: {qr_code}")
    try:
        product = Product.objects.get(qr_code=qr_code)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=404)

# -----------------------
# ✅ Registration Verification Views
# -----------------------

def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@api_view(['POST'])
@permission_classes([AllowAny])
def request_verification(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'detail': 'Email and password required'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'detail': 'User already exists'}, status=400)

    code = generate_code()

    send_mail(
        'Your QR Supply Verification Code',
        f'Your verification code is: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

    return Response({'detail': 'Verification code sent to email', 'code': code})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration(request):
    email = request.data.get('email')
    password = request.data.get('password')
    code = request.data.get('code')

    if not all([email, password, code]):
        return Response({'detail': 'All fields are required'}, status=400)

    user = User.objects.create_user(email=email, password=password)
    user.is_verified = True
    user.verification_code = None
    user.save()

    return Response({'detail': 'User created and verified'}, status=201)

# -----------------------
# ✅ Product CRUD with Logging
# -----------------------

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
@parser_classes([JSONParser, MultiPartParser, FormParser])
def product_detail(request, pk):
    print(f"product_detail view hit with method {request.method}")
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=404)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        old_quantity = product.quantity
        serializer = ProductSerializer(product, data=request.data, partial=True)

        if serializer.is_valid():
            updated_product = serializer.save()
            new_quantity = updated_product.quantity

            if new_quantity != old_quantity:
                StockHistory.objects.create(
                    product=product,
                    change_type='in' if new_quantity > old_quantity else 'out',
                    quantity_changed=abs(new_quantity - old_quantity)
                )

            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=204)

# -----------------------
# ✅ Stock In/Out via Button
# -----------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def stock_update(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        change_type = request.data.get('action')  # 'in' or 'out'
        qty = int(request.data.get('quantity'))

        if change_type == 'in':
            if product.quantity + qty > product.max_capacity:
                return Response({'detail': 'Exceeds max capacity'}, status=400)
            product.quantity += qty
        elif change_type == 'out':
            if product.quantity - qty < 0:
                return Response({'detail': 'Not enough stock'}, status=400)
            product.quantity -= qty
        else:
            return Response({'detail': 'Invalid action'}, status=400)

        product.save()

        StockHistory.objects.create(
            product=product,
            change_type=change_type,
            quantity_changed=qty
        )

        return Response({'detail': f'Stock {change_type} successful'}, status=200)

    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=404)

# -----------------------
# ✅ Total Stock
# -----------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def total_stock(request):
    total = Product.objects.aggregate(total=models.Sum('quantity'))['total'] or 0
    return Response({'total_stock': total})

# -----------------------
# ✅ Product History (by QR)
# -----------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def product_history(request, qr_code):
    try:
        product = Product.objects.get(qr_code=qr_code)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    history = StockHistory.objects.filter(product=product).order_by('-timestamp')
    serializer = StockHistorySerializer(history, many=True)
    return Response(serializer.data)

# -----------------------
# ✅ Run Migrations Endpoint (optional, dev only)
# -----------------------

@api_view(['GET'])
def run_migrations(request):
    try:
        call_command('makemigrations', 'inventory', interactive=False)
        call_command('migrate', interactive=False)
        return JsonResponse({"status": "✅ Migrations completed successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
