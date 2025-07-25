from . import service_ticket_bp
from .schemas import service_ticket_schema, service_tickets_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import ServiceTicket, db, Customer, Mechanic


# POST '/': Pass in all the required information to create the service_ticket.
@service_ticket_bp.route("/", methods=["POST"])
def create_service_ticket():
    try:
        print(service_ticket_schema.fields)
        ticket = service_ticket_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer_id = ticket.get("customer_id")
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error":"Customer not found"}), 404
    
    new_ticket = ServiceTicket(**ticket)
    db.session.add(new_ticket)
    db.session.commit()
    
    return service_ticket_schema.jsonify(new_ticket), 201
        
# PUT '/<ticket_id>/assign-mechanic/<mechanic-id>: Adds a relationship between a service ticket and the mechanics. (Reminder: use your relationship attributes! They allow you the treat the relationship like a list, able to append a Mechanic to the mechanics list).
@service_ticket_bp.route("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"])
def assign_mechanic(ticket_id, mechanic_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not ticket:
        return jsonify({"error": "Service Ticket not found"}), 404
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Check if mechanic is alerady assigned to ticket
    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to service ticket"}), 200
    
    ticket.mechanics.append(mechanic)
    db.session.commit()

    return jsonify({"message":f"Mechanic {mechanic_id} added to Service Ticket #{ticket_id}"}), 200

# PUT '/<ticket_id>/remove-mechanic/<mechanic-id>: Removes the relationship from the service ticket and the mechanic.
@service_ticket_bp.route("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"])
def remove_mechanic(ticket_id, mechanic_id):
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
def get_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    
    return service_tickets_schema.jsonify(tickets), 200