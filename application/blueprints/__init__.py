from flask import Blueprint

customers_bp = Blueprint('customers', __name__)
mechanics_bp = Blueprint('mechanics', __name__)
tickets_bp = Blueprint('tickets', __name__)

from .import routes