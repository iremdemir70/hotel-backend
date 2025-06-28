from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from app.models import User
from app.utils.auth import generate_token
from flasgger import swag_from


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'},
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'country': {'type': 'string'},
                    'city': {'type': 'string'},
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        201: {
            'description': 'User registered successfully'
        },
        400: {
            'description': 'Missing fields'
        },
        409: {
            'description': 'Email already registered'
        }
    }
})
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    country = data.get("country", "")
    city = data.get("city", "")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        email=email,
        password_hash=hashed_pw,
        first_name=first_name,
        last_name=last_name,
        country=country,
        city=city
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Login successful with token'
        },
        401: {
            'description': 'Invalid credentials'
        }
    }
})
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user)
    return jsonify({"token": token, "user": {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_admin": user.is_admin
    }}), 200


#google login

@auth_bp.route("/google-login", methods=["POST"])
@swag_from({
    'tags': ['Auth'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'id_token': {
                        'type': 'string',
                        'description': 'Google tarafından verilen ID token'
                    }
                },
                'required': ['id_token']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Google login başarılı, token döndürüldü'
        },
        401: {
            'description': 'Geçersiz ID token'
        }
    }
})
def google_login():
    data = request.get_json()
    token = data.get("id_token")

    try:
        idinfo = id_token.verify_oauth2_token(token, grequests.Request(), audience=None)
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password_hash="",
                is_google_user=True
            )
            db.session.add(user)
            db.session.commit()

        jwt_token = generate_token(user)
        return jsonify({
            "token": jwt_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_admin
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 401