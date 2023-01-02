import re

def validate_email(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if not email:
        raise ValueError('Users must submit an email address')
    if not re.fullmatch(regex, email):
        raise ValueError("Invalid email")
    return email

def validate_phone(phone):
    regex = re.compile(r'^\+[0-9]*$')
    if not phone:
        raise ValueError('Usesr must submit a phone number')
    if not re.fullmatch(regex, phone):
        raise ValueError("Invalid phone, Phone number must be in this format: +1234567890")
    return phone

def validate_password(password):
    special_characters = "[~\!@#\$%\^&\*\(\)_\+{}\":;'\[\]]"
    if not password:
        raise ValueError('Users must submit a password')
    if not any(char.isdigit() for char in password) or not any(char.isalpha() for char in password) or not any(char in special_characters for char in password):
        raise ValueError('Passwords must contain letters, numbers and special characters.')
    if len(password) < 8:
        raise ValueError('Password must contain at least 8 characters')
    return password
