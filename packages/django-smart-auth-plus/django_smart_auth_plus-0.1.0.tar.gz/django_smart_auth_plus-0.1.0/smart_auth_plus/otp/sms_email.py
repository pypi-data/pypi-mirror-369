import random

def generate_otp(length=6):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_sms(phone_number, message):
    print(f"Sending SMS to {phone_number}: {message}")

def send_email(email, subject, message):
    print(f"Sending Email to {email}: {subject} - {message}")
