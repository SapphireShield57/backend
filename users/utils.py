import random
import string
from django.core.mail import send_mail

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase, k=5))

def send_verification_email(email, code):
    send_mail(
        subject='Your QR SupplyScan Verification Code',
        message=f'Your verification code is: {code}',
        from_email='qrsupplyscan@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )
