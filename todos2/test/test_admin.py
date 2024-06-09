from ..routers.admin import get_db, get_current_user
from fastapi import status
from .util import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_admin(test_todo):
    response = client.get("/admin/")
    assert response.status_code == 200
    assert response.json() == [{'title':'drawing',
                                'complete':False,'description':'art',
                                'priority':5,'owner_id':1,'id':1}]


def test_delete_admin(test_todo):

    response = client.delete("/admin/delete?todo_id=1")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


