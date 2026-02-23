from flask import Flask
from .extensions import ma
from .models import db
from .blueprints.Customers import customers_bp
from .blueprints.Mechanics import mechanics_bp
from .blueprints.Tickets import tickets_bp
from .blueprints.Inventory import inventory_bp
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

swagger_blueprints = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Mechanic Shop API"
    }
)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    ma.init_app(app)
    db.init_app(app)
    
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(tickets_bp, url_prefix='/tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(swagger_blueprints, url_prefix=SWAGGER_URL)
    
    return app