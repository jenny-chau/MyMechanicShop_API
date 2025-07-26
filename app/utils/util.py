from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
import jose

SECRET_KEY = 'DiN0SaUr'

def encode_token(customer_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return token

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1] # Get token from string "Bearer <token>"
            
        if not token:
            return jsonify({'error':'Token not found'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            customer_id = data['sub']
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'error': 'token has expired'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(customer_id, *args, **kwargs)
    
    return decorated