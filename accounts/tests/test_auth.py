import pytest

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


User = get_user_model()


@pytest.fixture
def api_client():
    """
    Return a DRF API client for testing API endpoints.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Create a test user.
    """
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123!",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Return an API client authenticated with a valid access token.
    """
    response = api_client.post(
        "/api/auth/login/",
        {
            "username": "testuser",
            "password": "TestPassword123!",
        },
        format="json",
    )

    access_token = response.data["access"]

    api_client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access_token}"
    )

    return api_client


@pytest.mark.django_db
class TestRegister:

    def test_register_success(self, api_client):
        """
        Test that a new user can register successfully.
        """
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            format="json",
        )

        assert response.status_code == 201

        assert User.objects.filter(
            username="newuser"
        ).exists()

    def test_register_duplicate_username(self, api_client, user):
        """
        Test that registration fails when username already exists.
        """
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "testuser",
                "email": "another@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            format="json",
        )

        assert response.status_code == 400

        assert response.data["status"] == "error"
        assert response.data["message"] == "Username already exists."

    def test_register_password_mismatch(self, api_client):
        """
        Test that registration fails when passwords do not match.
        """
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "DifferentPassword!",
            },
            format="json",
        )

        assert response.status_code == 400

        assert response.data["status"] == "error"
        assert response.data["message"] == "Passwords do not match."


@pytest.mark.django_db
class TestLogin:

    def test_login_success(self, api_client, user):
        """
        Test that a user can login successfully.

        Verifies:
        - HTTP 200 response.
        - Access token is returned.
        - User information is returned.
        - Refresh token cookie is created.
        """
        response = api_client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        assert response.status_code == 200

        assert "access" in response.data
        assert "user" in response.data

        assert response.data["user"]["username"] == "testuser"

        assert "refresh_token" in response.cookies

        refresh_cookie = response.cookies["refresh_token"]

        assert refresh_cookie["httponly"] is True

    def test_login_invalid_password(self, api_client, user):
        """
        Test that login fails with an incorrect password.
        """
        response = api_client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "WrongPassword!",
            },
            format="json",
        )

        assert response.status_code == 401

        assert "detail" in response.data or response.data


@pytest.mark.django_db
class TestRefresh:

    def test_refresh_success(self, api_client, user):
        """
        Test that a valid refresh token generates a new access token.
        """
        login_response = api_client.post(
            "/api/auth/login/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        assert login_response.status_code == 200

        assert "refresh_token" in login_response.cookies

        refresh_token = login_response.cookies["refresh_token"].value

        api_client.cookies["refresh_token"] = refresh_token

        response = api_client.post(
            "/api/auth/refresh/",
            format="json",
        )

        assert response.status_code == 200

        assert "access" in response.data

    def test_refresh_without_cookie(self, api_client):
        """
        Test that refresh fails when the refresh token cookie
        is missing.
        """
        response = api_client.post(
            "/api/auth/refresh/",
            format="json",
        )

        assert response.status_code == 400

        assert response.data["message"] == "Refresh token not found."


@pytest.mark.django_db
class TestLogout:

    def test_logout_success(self, authenticated_client):
        """
        Test that an authenticated user can logout.

        Verifies that the refresh token cookie is deleted.
        """
        response = authenticated_client.post(
            "/api/auth/logout/",
            format="json",
        )

        assert response.status_code == 200

        assert response.data["status"] == "success"

        assert response.data["message"] == "Logged out successfully."

        assert "refresh_token" in response.cookies

        refresh_cookie = response.cookies["refresh_token"]

        assert refresh_cookie["max-age"] == 0

    def test_logout_without_authentication(self, api_client):
        """
        Test that an unauthenticated user cannot logout.
        """
        response = api_client.post(
            "/api/auth/logout/",
            format="json",
        )

        assert response.status_code == 401

        assert response.data["detail"] == (
            "Authentication credentials were not provided."
        )


