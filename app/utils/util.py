from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps
from flask import request, jsonify
import jose
import os

SECRET_KEY = os.environ.get('SECRET_KEY') or 'Secret_key'

# Encode token when customer or mechanic logs in. Encodes extra piece of information for whether they are customer or mechanic.
def encode_token(customer_id, customer_or_mechanic):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        'iat': datetime.now(timezone.utc),
        'sub': str(customer_id),
        'type': str(customer_or_mechanic)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    
    return token

# Verify customer token
def token_required_customer(f):
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
            customer_or_mechanic = data['type']
            if customer_or_mechanic != 'customer':
                raise jose.exceptions.JWTError
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'error': 'token has expired'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(customer_id, *args, **kwargs)
    
    return decorated

# Verify mechanic token
def token_required_mechanic(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
            
        if not token:
            return jsonify({"error":'Token not found'}), 401
        
        try:
            data=jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            mechanic_id = data['sub']
            customer_or_mechanic = data['type']
            if customer_or_mechanic != 'mechanic':
                raise jose.exceptions.JWTError
        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'error':'token has expired'}), 401
        except jose.exceptions.JWTError:
            return jsonify({'error':'Invalid token'}), 401
        
        return f(mechanic_id, *args, **kwargs)
    return decorated