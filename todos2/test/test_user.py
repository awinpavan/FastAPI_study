from ..routers.user import get_db, get_current_user
from .util import *
from fastapi import status
from ..routers.auth import bcrypt_context


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user(test_users):
    response = client.get("/user/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'awinpavan'
    assert response.json()['id'] == 1
    assert response.json()['first_name'] == 'awin'
    assert response.json()['last_name'] == 'pavan'
    assert response.json()['phone_number'] == '9061185683'
    assert response.json()['email'] == 'awinpavan@gmail.com'


def test_password_change(test_users):
    request = {'password' : 'password', 'new_password' : 'olaamigoes'}
    response = client.put('/user/password', json = request)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id==1).first()
    assert bcrypt_context.verify(request.get('new_password'),model.hashed_password)


def test_phone_number(test_users):
    request = {'phone_number':'910903048098909'}
    response = client.put("/user/phone_no._add",json=request)
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id==1).first()
    assert response.status_code == 201
    assert model.phone_number == request.get('phone_number')



