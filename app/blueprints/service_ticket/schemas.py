from app.extensions import ma
from app.models import ServiceTicket, InventoryServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer = fields.Nested('CustomerSchema', exclude=['id', 'password'])
    mechanics = fields.Nested('MechanicSchema', many=True, exclude=['password', 'salary', 'id'])
    items = fields.Nested('InventoryServiceTicketSchema', exclude=['id', 'tickets'], many = True)
    class Meta:
        model = ServiceTicket
        include_relationships = True
        include_fk = True 
        
class EditServiceTicket(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')
        
class AddItems(ma.Schema):
    # Service Ticket ID
    ticket_id = fields.Int(required=True)
    # list of item, quantity
    item_quant = fields.Nested("ItemQuantSchema", many=True)
    
class ItemQuantSchema(ma.Schema):
    item_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    
class InventoryServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = InventoryServiceTicket
        include_relationships = True
    item = fields.Nested('InventorySchema', exclude=['id'])

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicket()
add_items_schema = AddItems()