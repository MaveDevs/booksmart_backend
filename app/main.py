from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="backend")

# Configuración de Admin:
# from app.db.session import engine
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)

@app.get("/")
def root():
    return {"message": "Welcome to backend", "status": "active"}


# Routers
app.include_router(api_router, prefix="/api/v1")