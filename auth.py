import os
import dotenv
import jwt
import datetime


def create_JWT(user):
    payload = {
        'user_id': user['uuid'],
        'role': user['role'],
        'exp': datetime.datetime.now() + datetime.timedelta(days=14)
    }
    token = jwt.encode(payload, os.getenv("SECRET"), algorithm='HS256')
    return token

def decodeJWT(jwt_encoded):
    try:
        ans = jwt.decode(jwt_encoded, os.getenv("SECRET"), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        ans = "Invalid"
    except jwt.InvalidTokenError:
        ans = "Invalid"
    return ans

