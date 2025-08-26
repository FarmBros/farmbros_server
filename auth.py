import datetime
import os
import base64
import json
import jwt


def create_JWT(user):
    payload = {
        'user_id': user['uuid'],
        'role': user['role'],
        'exp': datetime.datetime.now() + datetime.timedelta(days=14)
    }

    token = jwt.encode(payload, os.getenv("SECRET"), algorithm='HS256')
    return token

def decodeJWT(jwt_encoded, use_google_secret=False):
    try:
        if use_google_secret:
            ans = decode_google_jwt(jwt_encoded)
            return ans
        else:
            secret = os.getenv("SECRET")
            ans = jwt.decode(jwt_encoded, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        ans = "Invalid"
    except jwt.InvalidTokenError:
        ans = "Invalid"
    return ans


def decode_google_jwt(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        return {
            "status": "error",
            "message": "Invalid token",
        }

    base64_url = parts[1]

    # Replace URL-safe characters (same as JS)
    base64_str = base64_url.replace("-", "+").replace("_", "/")

    # Add padding
    padding = 4 - len(base64_str) % 4
    if padding != 4:
        base64_str += "=" * padding

    try:
        # Decode base64
        decoded_bytes = base64.b64decode(base64_str)

        # Parse JSON
        payload = json.loads(decoded_bytes.decode('utf-8'))

        issuers = ['accounts.google.com', 'https://accounts.google.com']
        if payload['iss'] not in issuers:
            return {
                "status": "error",
                "message": "Invalid issuer",
            }

        return {
            'status': 'success',
            'data': payload,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }