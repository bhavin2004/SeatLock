from fastapi.testclient import TestClient
from app.main import app
from fastapi import status
from app.database.dependencies import get_db
from unittest.mock import patch,MagicMock



client = TestClient(app)


def test_list_movies_accepts_limit_one():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.router.service.list_movies") as mock_list:
                mock_list.return_value = []
        
                response = client.get("/api/v1/movies?limit=1")
        
                assert response.status_code == status.HTTP_200_OK
        
                mock_list.assert_called_once()
        
                call_kwargs = mock_list.call_args.kwargs
        
                assert call_kwargs["db"] is fake_db

    finally: 
         app.dependency_overrides.pop(get_db,None)


def test_list_movies_rejects_limit_zero():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.service.list_movies") as mock_list:

                response = client.get("/api/v1/movies?limit=0")

                assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

                mock_list.assert_not_called()
    finally:
      app.dependency_overrides.pop(get_db,None)


def test_list_movies_accepts_max_limit():
    fake_db = MagicMock()

    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.service.list_movies") as mock_list:
            mock_list.return_value = []

            response = client.get("/api/v1/movies?limit=100")

            assert response.status_code == status.HTTP_200_OK

            mock_list.assert_called_once()

            call_args = mock_list.call_args.kwargs

            assert call_args['db'] is fake_db
            assert call_args['limit'] == 100
    finally:
      app.dependency_overrides.pop(get_db,None)