from application.extensions import ma
from application.models import Ticket

class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True
        
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

