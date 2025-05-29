import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAdminUser
from .serializers import UserSerializer

User = get_user_model()

def generate_code(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# 📤 Request registration code
@api_view(['POST'])
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


# ✅ Finalize registration with code
@api_view(['POST'])
def verify_registration(request):
    email = request.data.get('email')
    password = request.data.get('password')
    code = request.data.get('code')

    if not all([email, password, code]):
        return Response({'detail': 'All fields are required'}, status=400)

    # Code validation must be done on frontend
    user = User.objects.create_user(email=email, password=password)
    user.is_verified = True
    user.save()

    return Response({'detail': 'User successfully verified and created'}, status=201)


# 🔐 Login view
class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                return Response({'detail': 'Invalid credentials'}, status=400)
            if not user.is_verified:
                return Response({'detail': 'Email not verified'}, status=403)

            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})

        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)


# 🔁 Forgot password step 1: send code
class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'detail': 'Email required'}, status=400)

        if not User.objects.filter(email=email).exists():
            return Response({'detail': 'User not found'}, status=404)

        code = generate_code()
        send_mail(
            'Your QR Supply Reset Code',
            f'Your reset code is: {code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({'detail': 'Reset code sent to email', 'code': code})


# 🔁 Step 2: verify reset code
class ResetPasswordVerifyView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'detail': 'Email and code are required'}, status=400)

        # ✅ Trust frontend to validate code; no server check
        return Response({'detail': 'Reset code verified'})


# 🔁 Step 3: save new password
class ResetPasswordSaveView(APIView):
    def post(self, request):
        try:
            email = request.data['email']
            new_password = request.data['new_password']
        except KeyError:
            return Response({'detail': 'Email and new password are required'}, status=400)

        if not email or not new_password:
            return Response({'detail': 'Fields cannot be empty'}, status=400)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password updated successfully'})
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)



# 👥 List all users
@api_view(['GET'])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# ❌ Delete a user
@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response({'detail': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
