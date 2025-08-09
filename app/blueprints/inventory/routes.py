from . import inventory_db
from .schemas import inventory_schema, inventories_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Inventory, db, Mechanic
from app.utils.util import token_required_mechanic

# POST '/' : create item
@inventory_db.route("/", methods=["POST"])
@token_required_mechanic
def create_item(mechanic_id):
    # Verify mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Unauthorized Access'}), 400
    
    #  Load data from client side
    try:
        data = inventory_schema.load(request.json)
        data['name'] = data['name'].lower()
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Find exact same item in inventory list (item name is case insensitive)
    query = select(Inventory).where(Inventory.name == data['name'] and Inventory.price == data['price'])
    item = db.session.execute(query).scalars().all()
    
    if item:
        return jsonify({'message':'Item already exists'}), 400
    
    # Create new item if not already in the inventory list
    new_item = Inventory(**data)
    db.session.add(new_item)
    db.session.commit()
    
    return inventory_schema.jsonify(new_item), 201

# GET '/' : get all items
@inventory_db.route('/', methods=["GET"])
def get_items():
    query = select(Inventory)
    items = db.session.execute(query).scalars().all()
    
    return inventories_schema.jsonify(items), 200

# GET '/<int:item_id> : get item by id
@inventory_db.route('/<int:item_id>', methods=["GET"])
def get_item(item_id):
    item = db.session.get(Inventory, item_id)
    
    if not item:
        return jsonify({'error':'Item not found'}), 404
    
    return inventory_schema.jsonify(item), 200

# PUT '/<int:item_id> : update item
@inventory_db.route('/<int:item_id>', methods=["PUT"])
@token_required_mechanic
def update_item(mechanic_id, item_id):
    # Verify mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Unauthorized Access'}), 400
    
    # Load and validate data
    try:
        data = inventory_schema.load(request.json)
        data['name'] = data['name'].lower()
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Find item to update
    query = select(Inventory).where(Inventory.id == item_id)
    item = db.session.execute(query).scalar_one_or_none()
    
    if not item:
        return jsonify({'error':'Item not found'}), 404
    
    # Update item
    for key, value in data.items():
        if value:
            setattr(item, key, value)
        
    db.session.commit()
    
    return inventory_schema.jsonify(item), 200

# DELETE '/<int:item_id>' : delete item (and all instances of this item in service tickets)
@inventory_db.route('/<int:item_id>', methods=['DELETE'])
@token_required_mechanic
def delete_item(mechanic_id, item_id):
    # Verify mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Unauthorized Access'}), 400
    
    #  Get item
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({'error':'Item not found'}), 404
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message':'Item successfully deleted'}), 200