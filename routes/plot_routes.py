from typing import Annotated

from fastapi import APIRouter, Request, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from models import runner
from routes.user_routes import get_current_user
router = APIRouter(
    prefix="/plots",
    tags=["Plot"]
)

security = HTTPBearer()


@router.post("/test", response_model=None)
async def test_plot(
        request: Request,
        user: Annotated[dict, Depends(get_current_user)],
        session: Session = Depends(runner.get_db_session),
):
    # data = await request.json()
    return {
        "status": "success",
        "message": "Plot test successful",
    }