from application.extensions import ma
from application.models import Inventory

class InventorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True
        
inventory_schema = InventorySchema() 
inventorys_schema = InventorySchema(many=True)
login_schema = InventorySchema()