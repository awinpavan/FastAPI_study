from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from typing import Annotated
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Users
from ..database4 import sessionlocal
from .auth import get_current_user
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/user',
    tags=['/user']
)

template = Jinja2Templates(directory='template')


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class CreateUserRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class PhoneNumber(BaseModel):
    phone_number: int


@router.get("/", response_class=HTMLResponse)
async def change(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    response = template.TemplateResponse("password-change.html", {"request": request, "user": user})
    return response


@router.post("/", response_class=HTMLResponse)
async def change_user_pass(request: Request, username: str = Form(...), password: str = Form(...),
                           new_password: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    verify = db.query(Users).filter(Users.username == username).first()
    if verify is None or not bcrypt_context.verify(password, verify.hashed_password):
        msg = "Invalid Username or Password"
        return template.TemplateResponse("password-change.html", {"request": request, "msg": msg, "user":user})

    hashed_new_password = bcrypt_context.hash(new_password)
    verify.hashed_password = hashed_new_password
    db.add(verify)
    db.commit()
    msg = "Password Update Successful"
    return template.TemplateResponse("password-change.html", {"request": request, "msg": msg, "user":user})


@router.get('/user', status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication invalid')
    info = db.query(Users).filter(Users.id == user.get('id')).first()
    if info is None:
        raise HTTPException(status_code=404, detail='User not found')
    return info


@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def password_change(user: user_dependency, db: db_dependency, create_request: CreateUserRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication invalid')
    change = db.query(Users).filter(Users.id == user.get('id')).first()
    if not bcrypt_context.verify(create_request.password, change.hashed_password):
        raise HTTPException(status_code=401, detail='password change error')
    change.hashed_password = bcrypt_context.hash(create_request.new_password)
    db.add(change)
    db.commit()


@router.put("/phone_no._add", status_code=status.HTTP_201_CREATED)
async def phone_number(user: user_dependency, db: db_dependency, create: PhoneNumber):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication invalid')
    number_model = db.query(Users).filter(Users.id == user.get('id')).first()
    number_model.phone_number = create.phone_number
    db.add(number_model)
    db.commit()
