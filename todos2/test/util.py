from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database4 import base
import pytest
from fastapi.testclient import TestClient
from ..main3 import app
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"
client = TestClient(app)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return{'username':'awin','id':1,'user_role':'admin'}


@pytest.fixture
def test_todo():
    todo = Todos(
        title='drawing',
        description='art',
        complete=False,
        priority=5,
        owner_id=1,
        id=1
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos'))
        connection.commit()

@pytest.fixture()
def test_users():
    user = Users(
        username = 'awinpavan',
        first_name = 'awin',
        last_name = 'pavan',
        id = 1,
        email = 'awinpavan@gmail.com',
        hashed_password = bcrypt_context.hash('password'),
        role = 'admin',
        phone_number = 9061185683,
        is_active = True
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()

@pytest.fixture()
def test_user():
    user = Users(
        username = 'awinpavan',
        first_name = 'awin',
        last_name = 'pavan',
        id = 1,
        email = 'awinpavan@gmail.com',
        hashed_password = bcrypt_context.hash('password'),
        role = 'admin',
        phone_number = 9061185683,
        is_active = True
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM users'))
        connection.commit()


