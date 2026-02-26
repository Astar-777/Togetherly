from fastapi import FastAPI

from app.api import auth, rooms, queue

app = FastAPI()

routers = [
    auth.router,
    rooms.router,
    queue.router
]

for router in routers:
    app.include_router(router)
