from functools import wraps
from functools import wraps, partial
from fastapi import Request
from fastapi.responses import JSONResponse

import json

import auth

def jwt_required(permission_level):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)

            auth_token = auth_header.split(" ")[1]
            decoded_token = auth.decodeJWT(auth_token)
            if decoded_token == "Invalid":
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)
            role = decoded_token['role']
            if permission_level == 'admin' and role != 'admin':
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def jwt_required_with_id(permission_level):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, user_id=None, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)

            auth_token = auth_header.split(" ")[1]
            decoded_token = auth.decodeJWT(auth_token)
            if decoded_token == "Invalid":
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)
            role = decoded_token['role']
            if permission_level == 'admin' and role != 'admin':
                return JSONResponse({'message': 'Incorrect credentials'}, status_code=401)

            user_id = decoded_token['user_id']
            return await func(request, user_id, *args, **kwargs)

        return wrapper

    return decorator

