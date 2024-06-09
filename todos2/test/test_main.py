from fastapi.testclient import TestClient
from ..main3 import app
from fastapi import status

client = TestClient(app)


def test_health_check():
    response = client.get('/healthy')  # this is to work out the API end point
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status":"healthy"}

