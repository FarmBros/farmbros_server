from fastapi import FastAPI
from routes import user_routes, plot_routes

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(plot_routes.router)


@app.get("/")
def hello():
    return {"message": "Let's get farming 🚜🌾"}

