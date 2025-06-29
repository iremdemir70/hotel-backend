from functools import wraps
from flask import request, jsonify
import jwt
import os
from datetime import datetime, timedelta
from app.models import User

def generate_token(user):
    payload = {
        "user_id": user.id,  # ← sub yerine bunu koy
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=3)
    }
    token = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")
    return token



def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.replace("Bearer ", "")

        if not token:
            return jsonify({'error': 'Token eksik'}), 401

        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            user = User.query.get(data["user_id"])
            if not user or not user.is_admin:
                return jsonify({'error': 'Bu işlem sadece adminlere açıktır'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token süresi dolmuş'}), 401
        except Exception:
            return jsonify({'error': 'Geçersiz token'}), 401

        return f(*args, **kwargs)
    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            bearer = request.headers['Authorization']
            token = bearer.replace("Bearer ", "")

        if not token:
            return jsonify({'error': 'Token eksik'}), 401

        try:
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            user = User.query.get(data["user_id"])
            if not user:
                return jsonify({'error': 'Kullanıcı bulunamadı'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token süresi dolmuş'}), 401
        except Exception:
            return jsonify({'error': 'Geçersiz token'}), 401

        return f(user, *args, **kwargs)
    return decorated
