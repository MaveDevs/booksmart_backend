from fastapi import APIRouter
from app.api.v1.endpoints import login, users, establishments, services

api_router = APIRouter()

api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(establishments.router, prefix="/establishments", tags=["establishments"])
api_router.include_router(services.router, prefix="/services", tags=["services"])