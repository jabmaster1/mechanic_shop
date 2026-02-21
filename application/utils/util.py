import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = 'secret key'

def encode_token(id, role):
    payload = {
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow(),
        'sub': str(id),
        'role': role
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'message': 'Must be logged in to access.'}), 401

        parts = auth_header.split()
        if parts[0] != 'Bearer' or len(parts) != 2:
            return jsonify({'message': 'Invalid Authorization header format'}), 401

        token = parts[1]

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = int(payload['sub'])
            role = payload.get('role')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token.'}), 401

        return f(user_id, role, *args, **kwargs)
    return decorated

def mechanic_required(f):
    @wraps(f)
    def decorated(user_id, role, *args, **kwargs):
        if role != 'mechanic':
            return jsonify({'message': 'Mechanic access required.'}), 400
        return f(user_id, role, *args, **kwargs)
    return decorated