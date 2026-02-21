from .schemas import ticket_schema, tickets_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Ticket, Mechanic, db, Inventory
from . import tickets_bp
from ...extensions import limiter, cache
from ...utils.util import token_required, mechanic_required
#------------------ Ticket Routes ------------------
# CREATE ticket
@tickets_bp.route('/', methods=['POST'])
@token_required
@mechanic_required
def create_ticket(id, role):
    try:
        new_ticket = ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
          
    db.session.add(new_ticket)
    db.session.commit()
    
    return ticket_schema.jsonify(new_ticket), 201

# ASSIGN mechanic to ticket
@tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@token_required
@mechanic_required
def assign_mechanic(id, role,ticket_id, mechanic_id):
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
@token_required
@mechanic_required
def remove_mechanic(id, role,ticket_id, mechanic_id):
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
@token_required
@mechanic_required
def get_all_tickets(id, role):
    query = select(Ticket)
    all_tickets = db.session.execute(query).scalars().all()
    
    return tickets_schema.jsonify(all_tickets), 200

# UPDATE ticket
@tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@token_required
@mechanic_required
def update_ticket_mechanics(id, role,ticket_id):
    ticket = db.session.get(Ticket, ticket_id)
    
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404
    
    data = request.json
    add_ids = data.get('add_ids', [])
    remove_ids = data.get('remove_ids', [])
    
    # ADD mechanics
    for mechanic_id in add_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    # REMOVE mechanics
    for mechanic_id in remove_ids:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    db.session.commit()
    
    return ticket_schema.jsonify(ticket), 200

# Get My Tickets (Logged in Customer)
@tickets_bp.route('/my-tickets', methods=['GET'])
@token_required

def get_my_tickets(id, role):
    if role != 'customer':
        return jsonify({'error': 'Must be a customer to view your tickets.'})
    
    query = select(Ticket).where(Ticket.customer_id == id)
    my_tickets = db.session.execute(query).scalars().all()
    return tickets_schema.jsonify(my_tickets), 200

# Assign Inventory item to Ticket
@tickets_bp.route('/<int:ticket_id>/add-part/<int:inventory_id>', methods=['POST'])
@token_required
@mechanic_required
def assign_inventory_to_ticket(id, role, inventory_id, ticket_id):
    inventory = db.session.get(Inventory, inventory_id)
    if not inventory:
        return jsonify({'error': 'Inventory item not found.'}), 404
    
    ticket = db.session.get(Ticket, ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404
    
    inventory.tickets.append(ticket)
    db.session.commit()
    
    return jsonify({'message': 'Inventory item assigned to ticket successfully.'})

