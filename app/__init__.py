from flask import Flask
from .models import db
from .extensions import ma, limiter, cache
from .blueprints.customers import customers_bp
from .blueprints.mechanic import mechanics_bp
from .blueprints.service_ticket import service_ticket_bp
from .blueprints.inventory import inventory_db

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')
    
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_ticket_bp, url_prefix="/serviceticket")
    app.register_blueprint(inventory_db, url_prefix="/inventory")

    return app