from fastapi import FastAPI
from routes import user_routes, farm_routes, plot_routes

from models import runner
import asyncio

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(farm_routes.router)
app.include_router(plot_routes.router)


@app.get("/")
def hello():
    return {"message": "Let's get farming 🚜🌾"}

#TODO: add security
@app.get("/db")
async def setup_db():
    await runner.init_db()
    return {"message": "Database setup <UNK>"}

