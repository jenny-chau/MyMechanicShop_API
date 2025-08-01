from app.extensions import ma
from app.models import Mechanic

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True, exclude=['password', 'salary']) # Exclude password and salary when getting information for multiple mechanics
login_schema = MechanicSchema(exclude=['name', 'phone', 'salary'])