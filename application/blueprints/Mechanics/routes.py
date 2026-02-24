from .schemas import mechanic_schema, mechanics_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func
from application.models import Mechanic, db, ticket_mechanic
from . import mechanics_bp
from ...extensions import limiter, cache
from ...utils.util import token_required, encode_token, mechanic_required

#------------------ Mechanic Routes ------------------
# CREATE mechanic
@mechanics_bp.route('/', methods=['POST'])
@limiter.limit('5 per day')
def create_mechanic():
    try:
        new_mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == new_mechanic.email)
    existing_mechanic = db.session.execute(query).scalars().first()
    
    if existing_mechanic:
        return jsonify({'message': 'Mechanic with this email already exists.'}), 400
    
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201

# LOGIN Mechanic
@mechanics_bp.route('/login', methods=['POST'])
def login_mechanic():
    try:
        credentials = login_schema.load(request.json)
        email = credentials.email
        password = credentials.password
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == email)
    mechanic = db.session.execute(query).scalars().first()
    
    if mechanic and mechanic.password == password:
        token = encode_token(mechanic.id, 'mechanic')
        
        response = {
            "status": "success",
            "message": "Mechanic logged in successfully.",
            "token": token
        }
        return jsonify(response), 200
    else: 
        return jsonify({'error': 'Invalid email or password.'}), 400


# GET all mechanics
@mechanics_bp.route('/', methods=['GET'])
@token_required
@mechanic_required
def get_all_mechanics(id, role):
    query = select(Mechanic)
    all_mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(all_mechanics), 200

# GET mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@token_required
@mechanic_required
def get_mechanic_by_id(id, role, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    else:
        return jsonify({'error': 'Mechanic not found.'}), 400
    
# UPDATE mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@token_required
@mechanic_required
def update_mechanic_by_id(id, role, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 400
    
    for key, value in request.json.items():
        if hasattr(mechanic, key):
            setattr(mechanic, key, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
    
# DELETE mechanic by ID
@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@token_required
@mechanic_required
def delete_mechanic_by_id(id, role, mechanic_id):
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({'message': 'Mechanic deleted successfully.'}), 200

# Get Mechanics ordered by number of tickets worked
@mechanics_bp.route('/top', methods=['GET'])
@token_required
@mechanic_required

def get_mechanics_by_ticket_count(id, role):
    query = (
        select(Mechanic, func.count(ticket_mechanic.c.ticket_id).label('ticket_count'))
        .join(ticket_mechanic, Mechanic.id == ticket_mechanic.c.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(ticket_mechanic.c.ticket_id).desc())
    )
    
    results = db.session.execute(query).all()
    
    mechanics_with_counts = [
        {
            'id': mechanic.id,
            'name': mechanic.name,
            'email': mechanic.email,
            'phone': mechanic.phone,
            'ticket_count': ticket_count
        }
        for mechanic, ticket_count in results
    ]
    
    return jsonify(mechanics_with_counts), 200

