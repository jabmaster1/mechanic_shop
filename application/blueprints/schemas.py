from application.extensions import ma
from application.models import Customer, Mechanic, Ticket

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        include_fk = True

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True
    
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)