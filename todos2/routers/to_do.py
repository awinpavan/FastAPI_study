from fastapi import APIRouter, Depends, HTTPException, status, Path, Request, Form
from typing import Annotated
from sqlalchemy.orm import Session
from ..models import Todos
from ..database4 import sessionlocal
from pydantic import BaseModel, Field
from .auth import get_current_user
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from starlette.responses import RedirectResponse
from starlette import status

router = APIRouter(
    prefix= '/todo',
    tags=['/todo']
)
templates = Jinja2Templates(directory='template')

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
async def read_all_user(request:Request, db:Session=Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.owner_id==user.get('id')).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user":user})


@router.get("/add-todo", response_class=HTMLResponse)
async def add_new_todo(request:Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-todo.html",{'request':request, "user":user})  # This is to get the page


@router.get("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request:Request, todo_id:int, db:Session=Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.id==todo_id).first()
    return templates.TemplateResponse("edit-todo.html",{"request":request, "todos":todos, "user":user})


@router.post("/add-todo",response_class=HTMLResponse)
async def create_new_todo(request:Request, title:str=Form(...), description:str=Form(...),
                          priority:int=Form(...),db:Session=Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = Todos()                                                # this is to edit the list in the page
    todo_model.title = title                                            # same endpoint but different parameters
    todo_model.description = description
    todo_model.priority = priority
    todo_model.owner_id = user.get('id')
    todo_model.complete = False

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/todo',status_code=status.HTTP_302_FOUND)


@router.post("/edit-todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_commit(request: Request, todo_id:int,title:str=Form(...),
                           description:str=Form(...), priority:int=Form(...), db:Session =Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    todo_model.title= title
    todo_model.description = description
    todo_model.priority = priority
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url='/todo', status_code=status.HTTP_302_FOUND)


@router.delete("/delete-todo/{todo_id}", response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        return RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()
    return RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)


@router.delete("/", response_class=HTMLResponse)
async def delete_todo_return(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user":user})


@router.get("/complete/{todo_id}",response_class=RedirectResponse)
async def complete_todo(request:Request, todo_id:int, db:Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todos).filter(Todos.id==todo_id).first()
    todo_model.complete = not todo_model.complete
    db.add(todo_model)
    db.commit()
    return RedirectResponse(url="/todo", status_code=status.HTTP_302_FOUND)







