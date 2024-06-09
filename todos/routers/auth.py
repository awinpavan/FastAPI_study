from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from ..models import *
from passlib.context import CryptContext
from ..database4 import sessionlocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "9ce3d51d5ff79d94d2cfc098ff7fbe739237ae41d58c8e8c19dfbaf655c32510"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
templates = Jinja2Templates(directory='template')



class LoginForm:
    def __init__(self, request:Request):
        self.request: Request = request     # larger info
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):  #
        form = await self.request.form()  # converts the class variables into a dict type that can be easily called
        self.username = form.get('username')
        self.password = form.get('password')


def get_password_hash(password):
    return bcrypt_context.hash(password)


def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(username: str, user_id: int, role:str,password:str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role':role, 'password':password}
    expire = datetime.utcnow() + expires_delta
    encode.update({'exp': expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


db_dependency = Annotated[Session, Depends(get_db)]
db_authentication = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/token")
async def login_for_access(response:Response, form_data: OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
    user_a = authenticate_user(form_data.username, form_data.password, db)  # to verify that the username and password
    if not user_a:                                                          # is correct in the given database
        return False
    token = create_access_token(user_a.username, user_a.id, user_a.role,user_a.hashed_password, timedelta(minutes=60))  # to get the jwt encode
    return {'access_token': token}


@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access(response=response, form_data=form, db=db)

        if not validate_user_cookie:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})



