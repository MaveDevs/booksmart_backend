from fastapi import APIRouter
from app.api.v1.endpoints import (
	agendas,
	appointments,
	establishments,
	login,
	messages,
	notifications,
	payments,
	plans,
	profiles,
	ratings,
	reports,
	rol,
	services,
	subscriptions,
	users,
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(establishments.router, prefix="/establishments", tags=["establishments"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(agendas.router, prefix="/agendas", tags=["agendas"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(rol.router, prefix="/roles", tags=["roles"])