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

async def google_signup(data, session) -> dict:
    try:
        data = auth.decode_google_jwt(data['token'])
        if data['status'] == "error":
            return data
        data = data['data']

        required_fields = ['sub', 'email', 'name']
        for field in required_fields:
            if not data.get(field):
                return {"status": "error", "message": f"{field} is required"}
        
        existing_google_user = select(user.User).where(user.User.google_id == data['sub'])
        result = await session.execute(existing_google_user)
        existing_google_user = result.scalar_one_or_none()
        if existing_google_user:
            existing_google_user.update_last_login()
            # existing_google_user.se
            token = auth.create_JWT(existing_google_user.to_dict())
            await session.commit()
            return {
                "status": "success",
                "message": "User logged in via Google",
                "data": token
            }

        existing_email_user = select(user.User).where(user.User.email == data['email'])
        result = await session.execute(existing_email_user)
        existing_email_user = result.scalar_one_or_none()
        if existing_email_user:
            if existing_email_user.google_id:
                return {"status": "error", "message": "Email already associated with another Google account"}
            else:
                existing_email_user.google_id = data['sub']
                existing_email_user.is_verified = True
                existing_email_user.update_last_login()
                # Update login_type based on existing auth methods
                if existing_email_user.password_hash:
                    existing_email_user.login_type = user.LoginType.BOTH
                else:
                    existing_email_user.login_type = user.LoginType.GOOGLE_AUTH
                token = auth.create_JWT(existing_email_user.to_dict())
                await session.commit()
                return {
                    "status": "success",
                    "message": "Google account linked to existing user",
                    "data": token
                }
        
        # Generate a username from email if not provided
        username = data.get('name', data['email'].split('@')[0])
        
        new_user = user.User(
            username=username,
            email=data['email'],
            google_id=data['sub'],
            first_name=data.get('given_name', ''),
            last_name=data.get('family_name', ''),
            full_name=data.get('name', ''),
            avatar_url=data.get('picture', ''),
            timezone=data.get('timezone', 'UTC'),
            language=data.get('language', 'en'),
            theme=data.get('theme', 'light'),
        )
        new_user.is_verified = data.get('email_verified', False)
        new_user.login_type = user.LoginType.GOOGLE_AUTH
        new_user.update_last_login()
        
        # if new_user.first_name and new_user.last_name:
        #     new_user.full_name = f"{new_user.first_name} {new_user.last_name}"
        
        session.add(new_user)
        token = auth.create_JWT(new_user.to_dict())

        await session.commit()

        return {
            "status": "success",
            "message": "User created via Google signup",
            "data": token
        }
    except Exception as e:
        await session.rollback()
        return {"status": "error", "message": str(e)}


