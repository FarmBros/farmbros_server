from typing import Annotated

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models import runner
from controllers import user_controller

router = APIRouter(
    prefix="/users",
    tags=["User"]
)

security = HTTPBearer()


@router.post("/create", response_model=None)
async def create_user(
        request: Request,
        session: Session = Depends(runner.get_db_session),
        ):
    data = await request.json()
    return await user_controller.create_user(data, session)

@router.post("/login", response_model=dict)
async def login_user(
        request: Request,
        session: Session = Depends(runner.get_db_session),
        ):
    data = await request.json()
    return await user_controller.login_user(data, session)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: Session = Depends(runner.get_db_session)
        ):
    token = credentials.credentials
    user_data = await user_controller.get_user_from_token(token, session)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user_data

async def get_admin_user(
        user: Annotated[dict, Depends(get_current_user)],
        ):
    if user['status'] == 'error':
        raise HTTPException(status_code=401, detail=user['message'])
    user = user['user']
    if user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

@router.post("/me", response_model=None)
async def verify_user(
        user: Annotated[dict, Depends(get_current_user)],
        ):
    return user

@router.post("/admin", response_model=None)
async def verify_admin(
        user: Annotated[dict, Depends(get_admin_user)],
        ):
    return user


# @router.post("/get_user", response_model=dict)
# async def get_user(
#         request: Request,
#         session: Session = Depends(runner.get_db_session),
#         user_id: int = Depends(runner.get_current_user_id)
#         ):
#     return await user_controller.get_user(user_id, session)

