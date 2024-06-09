from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models import Users
from passlib.context import CryptContext
from ..database4 import sessionlocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "9ce3d51d5ff79d94d2cfc098ff7fbe739237ae41d58c8e8c19dfbaf655c32510"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')
templates = Jinja2Templates(directory='template')


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number:int


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
db_authentication = Annotated[OAuth2PasswordRequestForm, Depends()]


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    pass_valid = bcrypt_context.verify(password, user.hashed_password)
    if not pass_valid:
        return False
    return user


def create_access_token(username: str, user_id: int, role:str,password:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role':role, 'password':password}
    expire = datetime.utcnow() + expires_delta
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        user_password = payload.get('password')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        return {'username': username, 'id': user_id, 'user_role': user_role, 'password':user_password}
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user: {str(e)}')


@router.post("/token", response_model=Token)
async def login_for_access(form_data: db_authentication, db: db_dependency):
    user_a = authenticate_user(form_data.username, form_data.password, db)  # to verify that the username and password
    if not user_a:                                                          # is correct in the given database
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
    token = create_access_token(user_a.username, user_a.id, user_a.role,user_a.hashed_password, timedelta(minutes=200))  # to get the jwt encode
    return {'access_token': token, 'token_type': 'bearer'}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True,
        phone_number = create_user_request.phone_number
    )
    db.add(create_user_model)
    db.commit()


@router.get("/",response_class=HTMLResponse)
async def authentication_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})


@router.get("/register", response_class=HTMLResponse)
async def register(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})
