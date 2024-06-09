from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Users
from ..database4 import sessionlocal
from .auth import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['/user']
)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt = CryptContext(schemes=['bcrypt'], deprecated='auto')


class CreateUserRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class PhoneNumber(BaseModel):
    phone_number: int


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
    if not bcrypt.verify(create_request.password, change.hashed_password):
        raise HTTPException(status_code=401, detail='password change error')
    change.hashed_password = bcrypt.hash(create_request.new_password)
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


