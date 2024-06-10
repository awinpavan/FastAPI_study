from fastapi import FastAPI
from starlette import status
from .models import base
from .database4 import engine
from .routers import auth, to_do, admin, user
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
app = FastAPI()

base.metadata.create_all(bind = engine)
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.get("/")
async def root():
    return RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
def health_check():
    return {"status":"healthy"}


app.include_router(auth.router)
app.include_router(to_do.router)
app.include_router(admin.router)
app.include_router(user.router)


