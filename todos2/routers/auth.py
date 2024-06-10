from datetime import timedelta, datetime
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Request, Response, Form
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse
from ..models import Users
from passlib.context import CryptContext
from ..database4 import sessionlocal
from fastapi.security import OAuth2PasswordRequestForm
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

async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        if username is None or user_id is None:
            return None
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=404, detail="Not found")


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def get_password_hash(password):
    return bcrypt_context.hash(password)


def create_access_token(username:str, id:int, expires_delta: Optional[timedelta] = None):
        encode = {"sub":username, "id":id}
        expire_time = datetime.utcnow()+expires_delta
        encode.update({"exp":expire_time})
        return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
db_authentication = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.get("/", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/logout", response_class=HTMLResponse)
async def log_out(request:Request):
    msg = "Logout Successfully"
    response = templates.TemplateResponse("login.html", {"request":request, "msg":msg})
    response.delete_cookie(key="access_token")
    return response


@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return False
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username,
                                user.id,
                                expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)

    return True



@router.post("/", response_class=HTMLResponse)
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)

        if not validate_user_cookie :
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_user(request:Request, email:str=Form(...), username:str=Form(...),
                        first_name:str=Form(...), last_name:str=Form(...),password:str=Form(...),
                        password2:str=Form(...), db:Session=Depends(get_db)):
    validation = db.query(Users).filter(Users.username==username).first()
    validation_2 = db.query(Users).filter(Users.email == email).first()

    if password != password2 or validation is not None or validation_2 is not None:
        msg = "Invalid registration request"
        return templates.TemplateResponse("register.html", {"request":request, "msg":msg})
    user_model = Users()
    user_model.username = username
    user_model.first_name = first_name
    user_model.last_name = last_name
    user_model.email = email
    hash_password = get_password_hash(password)
    user_model.hashed_password = hash_password
    user_model.is_active = True

    db.add(user_model)
    db.commit()

    msg = "User successfully created"
    return templates.TemplateResponse("login.html", {"request":request, "msg":msg})
