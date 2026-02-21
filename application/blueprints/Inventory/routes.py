from .schemas import inventory_schema, inventorys_schema, login_schema
from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Inventory, db, Ticket
from . import inventory_bp
from ...extensions import limiter, cache
from ...utils.util import mechanic_required, token_required

#------------------ inventory Routes ------------------
# CREATE inventory item
@inventory_bp.route('/create', methods=['POST'])
@token_required
@mechanic_required
def create_inventory(name, price):
    try:
        new_inventory = inventory_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Inventory).where(Inventory.name == new_inventory.name)
    existing_inventory = db.session.execute(query).scalars().first()
    
    if existing_inventory:
        return jsonify({'error': 'inventory with this name already exists.'}), 400
    
    db.session.add(new_inventory)
    db.session.commit()
    
    return inventory_schema.jsonify(new_inventory), 201

# GET all inventory items
@inventory_bp.route('/', methods=['GET'])
@token_required
def get_all_inventorys(id, role):
    query = select(Inventory)
    all_inventorys = db.session.execute(query).scalars().all()
    
    return inventorys_schema.jsonify(all_inventorys), 200

# GET inventory item by ID
@inventory_bp.route('/<int:inventory_id>', methods=['GET'])
@token_required
def get_inventory_by_id(id, role, inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if inventory:
        return inventory_schema.jsonify(inventory), 200
    else:
        return jsonify({'error': 'inventory not found.'}), 400
    
# UPDATE inventory by ID
@inventory_bp.route('/<int:inventory_id>', methods=['PUT'])
@token_required
@mechanic_required
def update_inventory_by_id(id, role, inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if not inventory:
        return jsonify({'error': 'inventory not found.'}), 400
    
    for key, value in request.json.items():
        if hasattr(inventory, key):
            setattr(inventory, key, value)
        
    db.session.commit()
    return inventory_schema.jsonify(inventory), 200
    
# DELETE inventory by ID
@inventory_bp.route('/<int:inventory_id>', methods=['DELETE'])
@token_required
@mechanic_required
def delete_inventory_by_id(id, role, inventory_id):
    inventory = db.session.get(Inventory, inventory_id)
    
    if not inventory:
        return jsonify({'error': 'inventory not found.'}), 404
    
    db.session.delete(inventory)
    db.session.commit()
    
    return jsonify({'message': 'inventory deleted successfully.'}), 200

