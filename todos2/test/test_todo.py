from ..routers.to_do import get_db, get_current_user
from fastapi import status
from .util import *


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_all(test_todo):
    response = client.get("/todo/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title':'drawing',
                                'complete':False,'description':'art',
                                'priority':5,'owner_id':1,'id':1}]


def test_get_one_all(test_todo):
    response = client.get("/todo/todo/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title':'drawing',
                                'complete':False,'description':'art',
                                'priority':5,'owner_id':1,'id':1}


def test_get_one_all_not_fount(test_todo):
    response = client.get("/todo/todo/999")
    assert response.status_code == 404
    assert response.json() == {'detail':'Todo not found'}


def test_post(test_todo):
    request={'title':'running','complete':False,
             'description':'marathone',
             'priority':5}
    response = client.post("/todo/todo", json=request)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id==2).first()
    assert model.title == request.get('title')
    assert model.description == request.get('description')
    assert model.complete == request.get('complete')
    assert model.priority == request.get('priority')


def test_put(test_todo):
    request={'title':'swimming','complete':False,
             'description':'olympic',
             'priority':5
             }
    response = client.put("/todo/todo/1", json = request)
    assert response.status_code == status.HTTP_202_ACCEPTED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id==1).first()
    assert model.title == request.get('title')
    assert model.complete == False
    assert model.description == 'olympic'
    assert model.priority == 5


def test_delete_todo(test_todo):
    response = client.delete("/todo/todo/1")
    assert response.status_code == 204
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

