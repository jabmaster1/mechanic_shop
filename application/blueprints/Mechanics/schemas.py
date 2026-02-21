from application.extensions import ma
from application.models import Mechanic

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True
        
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
login_schema = MechanicSchema(exclude=['id', 'name', 'phone', 'salary'])
