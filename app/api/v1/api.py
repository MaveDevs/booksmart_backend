from fastapi import APIRouter
from app.api.v1.endpoints import (
	agendas,
	analytics,
	appointments,
	auto_notifications,
	establishments,
	login,
	messages,
	notifications,
	payments,
	plan_features,
	plans,
	profiles,
	push_subscriptions,
	ratings,
	reports,
	special_closures,
	rol,
	services,
	subscriptions,
	users,
	workers,
	ws,
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(establishments.router, prefix="/establishments", tags=["establishments"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(workers.router, prefix="/workers", tags=["workers"])
api_router.include_router(agendas.router, prefix="/agendas", tags=["agendas"])
api_router.include_router(special_closures.router, prefix="/special-closures", tags=["special-closures"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(auto_notifications.router, prefix="/auto-notifications", tags=["auto-notifications"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(plan_features.router, prefix="/plan-features", tags=["plan-features"])
api_router.include_router(plans.router, prefix="/plans", tags=["plans"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(rol.router, prefix="/roles", tags=["roles"])
api_router.include_router(push_subscriptions.router, prefix="/push-subscriptions", tags=["push-subscriptions"])

# WebSocket route (no prefix — it's already /ws inside the router)
api_router.include_router(ws.router, tags=["websocket"])