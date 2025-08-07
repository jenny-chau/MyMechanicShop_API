from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema, edit_service_ticket_schema, add_items_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTicket, db, Customer, Mechanic, Inventory, InventoryServiceTicket
from app.extensions import cache
from app.extensions import limiter
from app.utils.util import token_required_mechanic, token_required_customer


# POST '/': Pass in all the required information to create the service_ticket.
@service_ticket_bp.route("/", methods=["POST"])
@limiter.limit('20 per hour') # Prevent too many service tickets from being created at once
@token_required_customer #required customer log in to submit a service request
def create_service_ticket(customer_id):
    try:
        ticket = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error":"Customer not found"}), 404
    
    new_ticket = ServiceTicket(**ticket, customer_id=customer.id)
    db.session.add(new_ticket)
    customer.tickets.append(new_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_ticket), 201
        
# PUT '/<ticket_id>/assign-mechanic: Adds a relationship between a service ticket and the logged in mechanics. For assigning other mechanics, use the '/<int:ticket_id>/edit' route to edit.
@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic", methods=["PUT"])
@token_required_mechanic
def assign_mechanic(mechanic_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Check if mechanic is already assigned to ticket
    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to service ticket"}), 200
    
    ticket.mechanics.append(mechanic)
    db.session.commit()

    return jsonify({"message":f"Mechanic {mechanic_id} added to Service Ticket #{ticket_id}"}), 200

# PUT '/<ticket_id>/remove-mechanic: Removes the relationship from the service ticket and the logged in mechanic. For removing other mechanics, use the '/<int:ticket_id>/edit' route to edit.
@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic", methods=["PUT"])
@token_required_mechanic
def remove_mechanic(mechanic_id, ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    # Check if ticket or mechanic exists
    if not ticket or not mechanic:
        return jsonify({"error":"Service ticket or mechanic are not found"}), 404
    
    # Check if mechanic is assigned to ticket
    if mechanic not in ticket.mechanics:
        return jsonify({"error": "Mechanic not currently assigned to ticket"}), 400
    
    # Remove Mechanic from Ticket
    ticket.mechanics.remove(mechanic)    
    db.session.commit()
    
    return jsonify({"message":f"Mechanic successfully removed from Service Ticket #{ticket.id}"}), 200

# GET '/': Retrieves all service tickets.
@service_ticket_bp.route("/", methods=["GET"])
@cache.cached(timeout=60) # Cache all service ticket information for 1 min
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(tickets), 200

# PUT '/<int:ticket_id>/edit' : Add/removes mechanics from service ticket. Takes in 'remove_ids', and 'add_ids'. Logged in mechanic may add/remove other mechanics by their ids passed in.
@service_ticket_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
@token_required_mechanic
def edit_ticket(mechanic_id, ticket_id):
    # Verify logged in mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Unauthorized Access'}), 400
    
    # Get service ticket
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not ticket:
        return jsonify({'error':'no ticket found'}), 404
    
    # Load client side data
    try:
        ticket_edits = edit_service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Loop through add list to add each mechanic
    for mech_id in ticket_edits['add_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mech_id)
        mechanic = db.session.execute(query).scalar_one_or_none()
        
        # Check mechanic exists
        if not mechanic:
            return jsonify({'error':'One or more mechanics not found'}), 404
        
        # Add only if mechanic is not already in the list
        if mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)
            
    # Loop through add list to add each mechanic   
    for mech_id in ticket_edits['remove_mechanic_ids']:
        query = select(Mechanic).where(Mechanic.id == mech_id)
        mechanic = db.session.execute(query).scalar_one_or_none()
        
        # Check mechanic exists
        if not mechanic:
            return jsonify({'error':'One or more mechanics not found'}), 404
        
        # Remove only if mechanic is in the list
        if mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)
    
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200
    
# PUT '/add_items' : Add item to service ticket
@service_ticket_bp.route('/add_items', methods=['PUT'])
@token_required_mechanic # Only mechanics can add items to service tickets
def add_items(mechanic_id):   
    # Verify logged in mechanic exists
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({'error': 'Unauthorized Access'}), 400
 
    # Load data input
    try:
        data = add_items_schema.load(request.json)
        ticket_id = data['ticket_id']
        items_quant = data['item_quant']
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Find service ticket
    ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not ticket:
        return jsonify({'error':'no ticket found'}), 404
    
    # Only allow mechanics working on the service ticket to add items to the ticket
    if mechanic not in ticket.mechanics:
        return jsonify({'error':'Not authorized to make adjustments to this ticket'}), 400
    
    # Add items
    for item in items_quant:
        if item['quantity'] <= 0:
            continue
        
        itm = db.session.get(Inventory, item['item_id'])
    
        if not itm:
            return jsonify({'error':'Item not found'}), 404

        # If trying to add an item already on the service ticket, add to the quantity already stored for that item
        found = False
        for inventory_serviceticket in ticket.items:
            if inventory_serviceticket.inventory_id == itm.id:
                inventory_serviceticket.quantity += item['quantity']
                found = True
                
        if found == False:
            ticket_item = InventoryServiceTicket(inventory_id = itm.id, service_ticket_id = ticket.id, quantity = item['quantity'])
            db.session.add(ticket_item)
    
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200    
    