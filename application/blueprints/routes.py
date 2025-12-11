from .schemas import customer_schema, customers_schema, mechanic_schema, mechanics_schema, ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Customer, db, Mechanic, Ticket
from . import customers_bp, mechanics_bp, tickets_bp

# ------------------ Customer Routes ------------------
# CREATE Customer
@customers_bp.route('/', methods=['POST'])
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

# GET all customers
@customers_bp.route('/', methods=['GET'])
def get_all_customers():
    query = select(Customer)
    all_customers = db.session.execute(query).scalars().all()
    
    return customers_schema.jsonify(all_customers), 200

# GET customer by ID
@customers_bp.route('/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = db.session.get(Customer, id)
    
    if customer:
        return customer_schema.jsonify(customer), 200
    else:
        return jsonify({'error': 'Customer not found.'}), 400
    
# UPDATE customer by ID
@customers_bp.route('/<int:id>', methods=['PUT'])
def update_customer_by_id(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404

    for key, value in request.json.items():
        if hasattr(customer, key):
            setattr(customer, key, value)
        
    db.session.commit()
    return customer_schema.jsonify(customer), 200

# DELETE customer by ID
@customers_bp.route('/<int:id>', methods=['DELETE'])
def delete_customer_by_id(id):
    customer = db.session.get(Customer, id)
    
    if not customer:
        return jsonify({'error': 'Customer not found.'}), 404
    
    db.session.delete(customer)
    db.session.commit()
    return jsonify({'message': 'Customer deleted succesfully.'}), 200

#------------------ Mechanic Routes ------------------
# CREATE mechanic
@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    try:
        new_mechanic = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Mechanic).where(Mechanic.email == new_mechanic.email)
    existing_mechanic = db.session.execute(query).scalars().first()
    
    if existing_mechanic:
        return jsonify({'error': 'Mechanic with this email already exists.'}), 400
    
    db.session.add(new_mechanic)
    db.session.commit()
    
    return mechanic_schema.jsonify(new_mechanic), 201

# GET all mechanics
@mechanics_bp.route('/', methods=['GET'])
def get_all_mechanics():
    query = select(Mechanic)
    all_mechanics = db.session.execute(query).scalars().all()
    
    return mechanics_schema.jsonify(all_mechanics), 200

# GET mechanic by ID
@mechanics_bp.route('/<int:id>', methods=['GET'])
def get_mechanic_by_id(id):
    mechanic = db.session.get(Mechanic, id)
    
    if mechanic:
        return mechanic_schema.jsonify(mechanic), 200
    else:
        return jsonify({'error': 'Mechanic not found.'}), 400
    
# UPDATE mechanic by ID
@mechanics_bp.route('/<int:id>', methods=['PUT'])
def update_mechanic_by_id(id):
    mechanic = db.session.get(Mechanic, id)
    
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 400
    
    for key, value in request.json.items():
        if hasattr(mechanic, key):
            setattr(mechanic, key, value)
        
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200
    
# DELETE mechanic by ID
@mechanics_bp.route('/<int:id>', methods=['DELETE'])
def delete_mechanic_by_id(id):
    mechanic = db.session.get(Mechanic, id)
    
    if not mechanic:
        return jsonify({'error': 'Mechanic not found.'}), 404
    
    db.session.delete(mechanic)
    db.session.commit()
    
    return jsonify({'message': 'Mechanic deleted successfully.'}), 200

#------------------ Ticket Routes ------------------
# CREATE ticket
@tickets_bp.route('/', methods=['POST'])
def create_ticket():
    try:
        new_ticket = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
          
    db.session.add(new_ticket)
    db.session.commit()
    
    return ticket_schema.jsonify(new_ticket), 201

# ASSIGN mechanic to ticket
@tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({'error': 'Ticket or mechanic not found.'}), 404

    if mechanic in ticket.mechanics:
        return jsonify({'message': 'Mechanic already assigned.'}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()

    return jsonify({'message': 'Mechanic assigned successfully.'}), 200

# REMOVE mechanic from ticket
@tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(Ticket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)

    if not ticket or not mechanic:
        return jsonify({'error': 'Ticket or mechanic not found.'}), 404

    if mechanic not in ticket.mechanics:
        return jsonify({'message': 'Mechanic not assigned to this ticket.'}), 200

    ticket.mechanics.remove(mechanic)
    db.session.commit()

    return jsonify({'message': 'Mechanic removed successfully.'}), 200

# GET all tickets
@tickets_bp.route('/', methods=['GET'])
def get_all_tickets():
    query = select(Ticket)
    all_tickets = db.session.execute(query).scalars().all()
    
    return tickets_schema.jsonify(all_tickets), 200