from .schemas import customer_schema, customers_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customer, db
from . import customers_bp
from ...extensions import limiter, cache
from ...utils.util import token_required, encode_token

# ------------------ Customer Routes ------------------
# CREATE Customer
@customers_bp.route('/', methods=['POST'])
@limiter.limit('5 per day')
def create_customer():
    try:
        new_customer = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == new_customer.email)
    existing_customer = db.session.execute(query).scalars().first()
    
    if existing_customer:
        return jsonify({'error': 'Customer with this email already exists.'}), 400
    
    db.session.add(new_customer)
    db.session.commit()
    
    return customer_schema.jsonify(new_customer), 201

# LOGIN Customer
@customers_bp.route('/login', methods=['POST'])
def login_customer():
    try:
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Customer).where(Customer.email == email)
    customer = db.session.execute(query).scalars().first()
    
    if customer and customer.password == password:
        token = encode_token(customer.id, 'customer')
        
        response = {
            "status": "success",
            "message": "Customer logged in successfully.",
            "token": token
        }
        return jsonify(response), 200
    else: 
        return jsonify({'error': 'Invalid email or password.'}), 400

# GET all customers
@customers_bp.route('/', methods=['GET'])
@token_required
def get_all_customers(id, role):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        query = select(Customer)
        all_customers = db.paginate(query, page=page, per_page=per_page)
        
    except:
        query = select(Customer)
        all_customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(all_customers), 200

# GET customer by ID
@customers_bp.route('/<int:customer_id>', methods=['GET'])
@token_required
def get_customer_by_id(id, role, customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    else:
        return jsonify({'error': 'Customer not found.'}), 400
    
# UPDATE customer by ID
@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer_by_id(id, role, customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    for key, value in request.json.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE customer by ID
@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer_by_id(id, role, customer_id):
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted succesfully.'}), 200