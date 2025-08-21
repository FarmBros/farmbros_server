import datetime
from models import user
import auth
from sqlalchemy.future import select
from services.validators import validate_user_data

async def create_user(data, session) -> dict:
    try:
        validated = validate_user_data(data)
        if not validated['is_valid']:
            return {
                "status": "error",
                "message": validated['error']
            }
        data = validated['data']
        new_user = user.User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip(),
            bio=data.get('bio', ''),
            avatar_url=data.get('avatar_url', ''),
            phone_number=data.get('phone_number', ''),
            timezone=data.get('timezone', 'UTC'),
            language=data.get('language', 'en'),
            theme=data.get('theme', 'light'),
            password=data.get('password', ''),
            # role=data.get('role', 'user'),
        )
        new_user.set_password(data['password'])
        session.add(new_user)
        await session.commit()
        return {
            "status": "success",
            "message": "User created"
        }
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}

async def login_user(data, session) -> dict:
    try:
        if not data.get('username') or not data.get('password'):
            return {"status": "error", "message": "Username and password are required"}
        data['username'] = data['username'].strip()
        data['password'] = data['password'].strip()
        user_instance = select(user.User).where(
            (user.User.username == data['username']) |
            (user.User.email == data['username'])
        )
        result = await session.execute(user_instance)
        user_instance = result.scalar_one_or_none()
        if not user_instance:
            return {"status": "error", "message": "User not found"}
        if not user_instance.check_password(data['password']):
            user_instance.increment_failed_login()
            return {"status": "error", "message": "Incorrect password"}

        user_instance.last_login = datetime.datetime.now()
        user_instance.first_login = False
        token = auth.create_JWT(user_instance.to_dict())

        await session.commit()


        return {
            "status": "success",
            "message": "User logged in",
            "data": token
        }
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}

async def get_user(user_id, session) -> dict:
    try:
        user_instance = await session.get(user.User, user_id)
        if not user_instance:
            return {"status": "error", "message": "User not found"}
        return {
            "status": "success",
            "user": user_instance.to_dict()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

async def get_user_from_token(token, session) -> dict:
    try:
        decoded = auth.decodeJWT(token)
        if decoded == "Invalid":
            return {"status": "error", "message": "Invalid token"}
        stmt = select(user.User).where(user.User.uuid == decoded['user_id'])
        user_instance = await session.execute(stmt)
        user_instance = user_instance.scalar_one_or_none()
        if not user_instance:
            return {"status": "error", "message": "Invalid token"}
        return {
            "status": "success",
            "user": user_instance.to_dict()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


