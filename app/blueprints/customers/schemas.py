from app.models import Customer
from app.extensions import ma

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True, exclude=['password']) # Exclude password when getting information for multiple customers
login_schema = CustomerSchema(exclude=['name', 'phone'])