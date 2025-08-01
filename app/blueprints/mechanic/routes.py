from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Mechanic, db
from sqlalchemy import select
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required_mechanic

# POST '/login' : Mechanic login
@mechanics_bp.route('/login', methods=['POST'])
def login():
    try:
        data = login_schema.load(request.json)
        username = data['email']
        password = data['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == username)
    mechanic = db.session.execute(query).scalar_one_or_none()
    
    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id, 'mechanic')
        
        response = {
            'status': 'Success',
            'message': 'Successfully logged in',
            'token': token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'error':'Inavlid username or password'}), 401

# POST '/' : Creates a new Mechanic
@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("10 per hour") # limit creation of mechanics
def add_mechanic():
    try:
        mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    #Check for existing mechanic with same email
    query = select(Mechanic).where(Mechanic.email == mechanic['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    
    if existing_mechanic:
        return jsonify({"error": "Email already registered"}), 400
    
    #create new mechanic
    new_mechanic = Mechanic(**mechanic)
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201


# GET '/': Retrieves all Mechanics (mechanic data excludes password and salary)
@mechanics_bp.route("/", methods=["GET"])
@cache.cached(timeout=60) # Cache all mechanics info for 1 min
def get_mechanics():
    query = select(Mechanic)
    
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200

# PUT '/':  Update Mechanic
@mechanics_bp.route("/", methods=["PUT"])
@token_required_mechanic
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    try:
        updates = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    #check for email dulplicate
    query = select(Mechanic).where(Mechanic.email == updates['email'])
    existing_mechanic = db.session.execute(query).scalars().all()
    
    if existing_mechanic and mechanic not in existing_mechanic:
        return jsonify({"error":"Duplicate email. Please use another email."}), 400
    
    #update mechanic
    for key, value in updates.items():
        setattr(mechanic, key, value)
    
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
    

# DELETE '/': Delete mechanic
@mechanics_bp.route("/", methods=["DELETE"])
@token_required_mechanic
def delete_mechanic(id):
    mechanic = db.session.get(Mechanic, id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({"message": "Mechanic deleted"}), 200


# GET '/ranked' : rank mechanics based on most service tickets worked on (mechanic data excludes password and salary)
@mechanics_bp.route('/ranked', methods=['GET'])
def ranked_mechanics():
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    
    mechanics.sort(key = lambda mechanic : len(mechanic.tickets), reverse = True)
    
    return mechanics_schema.jsonify(mechanics), 200