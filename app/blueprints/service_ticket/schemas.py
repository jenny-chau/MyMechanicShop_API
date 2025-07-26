from app.extensions import ma
from app.models import ServiceTicket
from marshmallow import fields

class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    customer = fields.Nested('CustomerSchema')
    mechanics = fields.Nested('MechanicSchema', many=True)
    class Meta:
        model = ServiceTicket
        fields = ('id', 'VIN', 'service_date', 'service_desc', 'customer_id', 'customer', 'mechanics')
        include_fk = True # Allows input of customer id
        
class EditServiceTicket(ma.Schema):
    add_mechanic_ids = fields.List(fields.Int(), required=True)
    remove_mechanic_ids = fields.List(fields.Int(), required=True)
    class Meta:
        fields = ('add_mechanic_ids', 'remove_mechanic_ids')

service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
edit_service_ticket_schema = EditServiceTicket()