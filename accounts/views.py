from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
# Response
from utils.response_transform import send_response

import logging
logger = logging.getLogger(__name__)

from .serializers import (
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    MeSerializer,
)


@api_view(['GET'])
def getRoutes(request):
    """
    Return a list of available API routes.

    """
    logger.info("Routes endpoint accessed.")

    routes = [
        'api/token',
        'api/token/refresh'
        'api/auth/register',
        'api/auth/logout'
    ]

    return Response(routes)


@api_view(['POST'])
def register_view(request):
    """
    Register a new user.

    POST:
        Body (JSON):
            - username (str): Required.
            - email (str): Valid email address, required.
            - password (str): Required, minimum 6 characters.
            - confirm_password (str): Must match `password`.

        Returns:
            - Success message with registered username and email on success.
            - Error message if any validation fails.
    """
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Log
    logger.info(
        "User registration attempt. username=%s email=%s",
        username,
        email,
    )

    # Check required fields
    if not username or not email or not password or not confirm_password:

        # log warning
        logger.warning(
            "Registration failed: Missing required fields. username=%s",
            username,
        )

        return send_response({
            'status': 'error',
            'message': 'All fields are required: username, email, password, confirm_password.'
        })

    # Email format validation
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError

    try:
        validate_email(email)
    except ValidationError:

        # Log
        logger.warning(
            "Registration failed: Invalid email. username=%s email=%s",
            username,
            email,
        )

        return send_response({
            'status': 'error',
            'message': 'Invalid email format.'
        })

    # Password confirmation
    if password != confirm_password:

        # log warning
        logger.warning(
            "Registration failed: Password mismatch. username=%s",
            username,
        )

        return send_response({
            'status': 'error',
            'message': 'Passwords do not match.'
        })

    # Password length (optional)
    if len(password) < 6:

        # Log warning
        logger.warning(
            "Registration failed: Password too short. username=%s",
            username,
        )

        return send_response({
            'status': 'error',
            'message': 'Password must be at least 6 characters long.'
        })

    # Unique username or email check
    if User.objects.filter(username=username).exists():

        # Log warning
        logger.warning(
            "Registration failed: Username already exists. username=%s",
            username,
        )

        return send_response({
            'status': 'error',
            'message': 'Username already exists.'
        })

    if User.objects.filter(email=email).exists():

        # Log warning
        logger.warning(
            "Registration failed: Email already exists. email=%s",
            email,
        )

        return send_response({
            'status': 'error',
            'message': 'Email already registered.'
        })

    # Create new user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        logger.info(
            "User registered successfully. id=%s username=%s",
            user.id,
            user.username,
        )

        return send_response({
            "status": "success",
            "message": "User registered successfully.",
            "user": {
                "username": user.username,
                "email": user.email,
            },
        }, status_code=201)

    except Exception:
        logger.exception(
            "Unexpected error during registration. username=%s",
            username,
        )

        return send_response({
            "status": "error",
            "message": "Internal server error."
        }, status_code=500)


@api_view(["POST"])
def logout_view(request):

    if request.user.is_authenticated:
        logger.info(
            "User logged out. id=%s username=%s",
            request.user.id,
            request.user.username,
        )
    else:
        logger.info("Anonymous logout request.")

    response = Response({
        "status": "success",
        "message": "Logged out successfully."
    })

    response.delete_cookie("refresh_token")

    return response


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me_view(request):

    if request.method == "GET":
        logger.info(
            "Profile retrieved. id=%s username=%s",
            request.user.id,
            request.user.username,
        )

        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    serializer = MeSerializer(
        request.user,
        data=request.data,
        partial=True,
    )

    serializer.is_valid(raise_exception=True)
    serializer.save()

    logger.info(
        "Profile updated. id=%s username=%s",
        request.user.id,
        request.user.username,
    )

    return Response(serializer.data)
