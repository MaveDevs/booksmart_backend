from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router

app = FastAPI(title="backend")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de Admin:
# from app.db.session import engine
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

@app.get("/")
def root():
    return {"message": "Welcome to backend", "status": "active"}


# Routers
app.include_router(api_router, prefix="/api/v1")