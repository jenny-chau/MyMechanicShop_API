from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from .schemas import customer_schema, customers_schema, login_schema
from app.blueprints.service_ticket.schemas import service_tickets_schema
from app.models import Customer, db
from app.extensions import limiter, cache
from . import customers_bp
from app.utils.util import encode_token, token_required_customer

# POST '/login' : Customer login
@customers_bp.route('/login', methods=['POST'])
def customer_login():
    try:
        credentials = login_schema.load(request.json)
        username = credentials['email']
        password = credentials['password']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == username)
    customer = db.session.execute(query).scalar_one_or_none()
    
    if customer and customer.password == password:
        auth_token = encode_token(customer.id, "customer")
        
        response = {
            'status': 'Success',
            'message': 'Successfully logged in',
            'auth_token': auth_token
        }
        
        return jsonify(response), 200
    
    else:
        return jsonify({'error':'Invalid username or password'}), 401
    
    

# POST '/' : Creates a new Customer
@customers_bp.route("/", methods=["POST"])
@limiter.limit("3 per hour") # Prevent too many customers from being made
def create_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == customer_data['email'])
    existing_customer = db.session.execute(query).scalars().all()
    if existing_customer:
        return jsonify({"error": "Customer exists already"}), 400
    
    new_customer = Customer(**customer_data)
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

# GET '/' : Gets all customers (can be paginated), customer data excludes passwords
@customers_bp.route("/", methods=["GET"])
@cache.cached(timeout=60) # Cache customer data for 1 min
def get_all_customers():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Customer)
        customers = db.paginate(query, page=page, per_page=per_page) # If page doesn't exist or error in inputs, exception will be run
        return customers_schema.jsonify(customers), 200
    except:
        query = select(Customer)
        customers = db.session.execute(query).scalars().all()
        return customers_schema.jsonify(customers), 200
        
    

# GET '/<customer_id>' : Gets specific customer based on id (log in not required)
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    return jsonify({"error": "Customer not found"}), 404

# PUT '/' : Updates customer data
@customers_bp.route("/", methods=["PUT"])
@limiter.limit("3 per day") # Prevent customers from updating their information too many times
@token_required_customer # Require login to update customer info
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error":"Customer not found"}), 404
        
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Check if email is being used already
    query = select(Customer).where(Customer.email == customer_data["email"])
    existing_email = db.session.execute(query).scalars().all()
    
    # Error only if email exists and belongs to another customer_id
    if existing_email and customer not in existing_email:
        return jsonify({"error": "email already exists. Please use another email."}), 400
    
    # Update customer entry
    for key, value in customer_data.items():
        setattr(customer, key, value)
    
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE '' : Delete customer based on customer id (and all their service tickets)
@customers_bp.route("/", methods=["DELETE"])
@token_required_customer # require customer login to delete account
def delete_customer(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    db.session.delete(customer)
    db.session.commit()
    
    return jsonify({"message": "Customer successfully deleted"}), 200


# GET '/my-tickets' : Get all service tickets associated with customer
@customers_bp.route('/my-tickets', methods=['GET'])
@token_required_customer
def get_tickets(customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({'error':'customer not found'}), 404
    
    return service_tickets_schema.jsonify(customer.tickets), 200
    
    