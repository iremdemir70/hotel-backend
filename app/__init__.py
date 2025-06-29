from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from dotenv import load_dotenv
import os
from .extensions import db, migrate
from .routes.auth_routes import auth_bp
from . import models
from .routes.hotel_routes import hotel_bp
from flask_jwt_extended import JWTManager


def create_app():
    load_dotenv()

    app = Flask(__name__)

    CORS(app, origins=[
    "http://localhost:4200", 
    "https://hotel-frontend-lemon.vercel.app"
], supports_credentials=True)


    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # ✅ JWT CONFIG
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"

    JWTManager(app)

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "A swagger API",
            "description": "powered by Flasgger",
            "version": "0.1"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/"
    }

    Swagger(app, template=swagger_template, config=swagger_config)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(hotel_bp)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return "Backend çalışıyor 🟢"

    return app
