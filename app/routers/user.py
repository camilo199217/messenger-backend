from fastapi import APIRouter, Depends
from app.dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas import user as user_schema

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.post("/")
async def get_or_create_user(
    data: user_schema.UserCreate, user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_or_create_user(
        user_data=data.user.model_dump(),
    )
