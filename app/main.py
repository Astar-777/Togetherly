from fastapi import FastAPI

from app.api import auth, rooms

app = FastAPI()

routers = [
    auth.router,
    rooms.router
]

for router in routers:
    app.include_router(router)
