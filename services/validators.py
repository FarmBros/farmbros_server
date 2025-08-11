from email_validator import validate_email, EmailNotValidError
import re

def validate_user_email(email:str) -> dict:
    try:
        validation = validate_email(email)
        email = validation.normalized
        return {
            'is_valid': True,
            'email': email
        }
    except EmailNotValidError as e:
        return {
            'is_valid': False,
            'error': str(e)
        }

def validate_username(username:str) -> dict:
    if not username or not isinstance(username, str):
        return {
            'is_valid': False,
            'error': "Username must be a non-empty string"
        }

    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    if re.match(pattern, username):
        return {
            'is_valid': True,
            'data': username.strip()
        }
    return {
        'is_valid': False,
        'error': "Username must be 3-20 characters long and can only contain letters, numbers, and underscores."
    }

def validate_phone_number(phone:str) -> dict:
    if not phone or not isinstance(phone, str):
        return {
            'is_valid': False,
            'error': "Phone number must be a non-empty string"
        }

    pattern = r'^\+?[1-9]\d{1,14}$'
    if re.match(pattern, phone):
        return {
            'is_valid': True,
            'data': phone.strip()
        }
    return {
        'is_valid': False,
        'error': "Phone number must be in E.164 format (e.g., +1234567890)"
    }

def validate_name(name:str) -> dict:
    if not name or not isinstance(name, str):
        return {
            'is_valid': False,
            'error': "Name must be a non-empty string"
        }

    pattern = r'^[a-zA-Z\s]{1,50}$'
    if re.match(pattern, name):
        return {
            'is_valid': True,
            'data': name.strip()
        }
    return {
        'is_valid': False,
        'error': "Name must be 1-50 characters long and can only contain letters and spaces."
    }

def validate_strong_password(password:str) -> dict:
    if not password or not isinstance(password, str):
        return {
            "is_valid": False,
            "error": "Password must be a non-empty string"
        }

    if len(password) < 8:
        return {
            "is_valid": False,
            "error": "Password must be at least 8 characters long"
        }

    patterns = [
        (r'[A-Z]', "Password must contain at least one uppercase letter"),
        (r'[a-z]', "Password must contain at least one lowercase letter"),
        (r'\d', "Password must contain at least one digit"),
        (r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', "Password must contain at least one special character")
    ]

    for pattern, error_msg in patterns:
        if not re.search(pattern, password):
            return {
                "is_valid": False,
                "error": error_msg
            }

    return {
        "is_valid": True,
        "data": password.strip()
    }

def validate_user_data(user:dict) -> dict:
    if not isinstance(user, dict):
        return {
            'is_valid': False,
            'error': "User data must be a dictionary"
        }

    email_validation = validate_user_email(user.get('email', ''))
    if not email_validation['is_valid']:
        return email_validation

    username_validation = validate_username(user.get('username', ''))
    if not username_validation['is_valid']:
        return username_validation

    phone_validation = validate_phone_number(user.get('phone_number', ''))
    if not phone_validation['is_valid']:
        return phone_validation

    if user['first_name']:
        fname_validation = validate_name(user.get('first_name', ''))
        if not fname_validation['is_valid']:
            return fname_validation
        user['first_name'] = fname_validation['data']

    if user['last_name']:
        lname_validation = validate_name(user.get('last_name', ''))
        if not lname_validation['is_valid']:
            return lname_validation
        user['last_name'] = lname_validation['data']

    password_validation = validate_strong_password(user.get('password', ''))
    if not password_validation['is_valid']:
        return password_validation

    user['email'] = email_validation['email']
    user['username'] = username_validation['data']
    user['phone_number'] = phone_validation['data']
    user['password'] = password_validation['data']
    return {
        'is_valid': True,
        'data': user
    }
