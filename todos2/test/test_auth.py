from ..routers.auth import get_db, authenticate_user, SECRET_KEY, ALGORITHM, create_access_token, get_current_user
from .util import *
from fastapi import status
from jose import jwt
from datetime import timedelta
import pytest
from fastapi import HTTPException


app.dependency_overrides[get_db] = override_get_db


def test_auth_user(test_users):
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id==1).first()
    authenticated_user = authenticate_user(model.username, 'password', db)
    assert authenticated_user is not None
    assert authenticated_user.username == model.username

    non_existent_user = authenticate_user('wrongname', 'password', db)
    assert non_existent_user == False

def test_access(test_users):
    username = 'awinpavan'
    id = 1
    role = 'admin'
    password = 'password'
    expire = timedelta(minutes=200)
    token = create_access_token(username, id, role, password, expire)

    decode = jwt.decode(token,SECRET_KEY,[ALGORITHM],options={'verify_signature':False})
    assert decode['sub'] == username
    assert decode['id'] == id
    assert decode['role'] == role


@pytest.mark.asyncio
async def test_get_user(test_users):
    encode = {'sub':'awinpavan', 'id':1, 'role':'admin'}
    token = jwt.encode(encode,SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token=token)
    assert user.get('username') == encode.get('sub')

@pytest.mark.asyncio
async def test_get_user_info():
    encode = {'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as exception:
        await get_current_user(token=token)
    assert exception.value.status_code == 401
    assert exception.value.detail == 'Could not validate user'

