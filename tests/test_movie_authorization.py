from datetime import datetime, timezone

from fastapi.testclient import TestClient
from app.main import app
from fastapi import status
from app.database.dependencies import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User, UserRole
from app.modules.movies.models import MovieStatus
from app.modules.movies.schemas import MovieResponse
import uuid
from unittest.mock import patch,MagicMock

client = TestClient(app)


fake_customer = User(
    id=uuid.uuid4(),
    email="customer-test@example.com",
    password_hash="not-a-real-hash",
    role=UserRole.CUSTOMER,
    is_active=True
)

fake_admin = User(
    id=uuid.uuid4(),
    email="admin-test@example.com",
    password_hash="not-a-real-hash",
    role=UserRole.ADMIN,
    is_active=True
)

def test_create_movie_without_token():
    response = client.post("/api/v1/movies",json={})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_customer_cannot_create_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_customer
    try:
        response = client.post("/api/v1/movies",json={})
        assert response.status_code == status.HTTP_403_FORBIDDEN
    finally:
        app.dependency_overrides.pop(get_current_user, None)

def test_admin_passes_movie_creation_authorization():
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    try:
        response = client.post("/api/v1/movies",json={})

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_current_user, None)

def test_admin_can_create_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    fake_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.router.service.create_movie") as mock_create:
            mock_create.return_value = MovieResponse(
                                            id=uuid.uuid4(),
                                            title="Interstellar",
                                            duration_minutes=169,
                                            release_date=None,
                                            description=None,
                                            poster_url=None,
                                            certification=None,
                                            status=MovieStatus.DRAFT,
                                            created_at=datetime.now(timezone.utc),
                                            updated_at=datetime.now(timezone.utc)
                                        )
            payload = {
                "title": "Interstellar",
                "duration_minutes": 169
            }
            response = client.post("/api/v1/movies", json=payload)

            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["title"] == "Interstellar"
            assert response.json()["status"] == "DRAFT"
            mock_create.assert_called_once()

            call_kwargs = mock_create.call_args.kwargs

            assert call_kwargs["db"] is fake_db
            assert call_kwargs["data"].title == "Interstellar"
            assert call_kwargs["data"].duration_minutes == 169
                                    
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)


def test_customer_cannot_update_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_customer
    try: 
        movie_id = uuid.uuid4()
        response = client.patch(
            f"/api/v1/movies/{movie_id}",
            json={"title": "Updated Movie"}
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        app.dependency_overrides.pop(get_current_user,None)

def test_customer_cannot_publish_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_customer
    try: 
        movie_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/movies/{movie_id}/publish"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        app.dependency_overrides.pop(get_current_user,None)


def test_customer_cannot_archive_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_customer
    try: 
        movie_id = uuid.uuid4()
        response = client.post(
            f"/api/v1/movies/{movie_id}/archive"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    finally:
        app.dependency_overrides.pop(get_current_user,None)


def test_admin_can_publish_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    fake_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.router.service.publish_movie") as mock_publish:
            movie_id = uuid.uuid4()
            mock_publish.return_value = MovieResponse(
                                            id=movie_id,
                                            title="Interstellar",
                                            duration_minutes=169,
                                            release_date=None,
                                            description=None,
                                            poster_url=None,
                                            certification=None,
                                            status=MovieStatus.PUBLISHED,
                                            created_at=datetime.now(timezone.utc),
                                            updated_at=datetime.now(timezone.utc)
                                        )

            response = client.post(f"/api/v1/movies/{movie_id}/publish")

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == "PUBLISHED"

            mock_publish.assert_called_once()
            call_args = mock_publish.call_args.args

            assert call_args[0] is fake_db
            assert call_args[1] == movie_id

    finally:
        app.dependency_overrides.pop(get_current_user,None)
        app.dependency_overrides.pop(get_db,None)


def test_admin_can_archive_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    fake_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.router.service.archive_movie") as mock_archive:
            movie_id = uuid.uuid4()
            mock_archive.return_value = MovieResponse(
                                            id=movie_id,
                                            title="Interstellar",
                                            duration_minutes=169,
                                            release_date=None,
                                            description=None,
                                            poster_url=None,
                                            certification=None,
                                            status=MovieStatus.ARCHIVED,
                                            created_at=datetime.now(timezone.utc),
                                            updated_at=datetime.now(timezone.utc)
                                        )

            response = client.post(f"/api/v1/movies/{movie_id}/archive")

            assert response.status_code == status.HTTP_200_OK
            assert response.json()["status"] == "ARCHIVED"

            mock_archive.assert_called_once()
            call_args = mock_archive.call_args.args

            assert call_args[0] is fake_db
            assert call_args[1] == movie_id

    finally:
        app.dependency_overrides.pop(get_current_user,None)
        app.dependency_overrides.pop(get_db,None)


def test_admin_can_update_movie():
    app.dependency_overrides[get_current_user] = lambda: fake_admin
    fake_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with patch("app.modules.movies.router.service.update_movie") as mock_update:
            movie_id = uuid.uuid4()
            mock_update.return_value = MovieResponse(
                                            id=movie_id,
                                            title="Interstellar 2",
                                            duration_minutes=169,
                                            release_date=None,
                                            description=None,
                                            poster_url=None,
                                            certification=None,
                                            status=MovieStatus.DRAFT,
                                            created_at=datetime.now(timezone.utc),
                                            updated_at=datetime.now(timezone.utc)
                                        )

            response = client.patch(f"/api/v1/movies/{movie_id}",json={"title": "Interstellar 2"})

            assert response.status_code == status.HTTP_200_OK

            mock_update.assert_called_once()
            call_args = mock_update.call_args.kwargs
            
            assert call_args["db"] is fake_db
            assert call_args["movie_id"] == movie_id
            assert call_args["data"].title == "Interstellar 2"

    finally:
        app.dependency_overrides.pop(get_current_user,None)
        app.dependency_overrides.pop(get_db,None)

