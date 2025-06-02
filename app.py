import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import IntegrityError
import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import io

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database for Render (PostgreSQL)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///local.db").replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

# Import models after app initialization
from models import Product, ConsumptionBill, BillItem, ReceptionSheet, ReceptionItem, DraftBill, DraftBillItem, DraftReception, DraftReceptionItem

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
# Initialize the app with the extension
db.init_app(app)

# Import models after app initialization
from models import Product, ConsumptionBill, BillItem, ReceptionSheet, ReceptionItem, DraftBill, DraftBillItem, DraftReception, DraftReceptionItem

def init_db():
    """Initialize database tables"""
    with app.app_context():
        # Create all tables
        db.create_all()

@app.route('/')
def index():
    """Dashboard with low stock alerts and recent activity"""
    # Get low stock products
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_stock).order_by(Product.quantity.asc()).all()
    
    # Get total products count
    total_products = Product.query.count()
    
    # Get recent consumption bills
    recent_bills = ConsumptionBill.query.order_by(ConsumptionBill.bill_date.desc()).limit(5).all()
    
    # Get recent receptions
    recent_receptions = ReceptionSheet.query.order_by(ReceptionSheet.reception_date.desc()).limit(5).all()
    
    return render_template('index.html', 
                         low_stock_products=low_stock_products,
                         total_products=total_products,
                         recent_bills=recent_bills,
                         recent_receptions=recent_receptions)

@app.route('/products')
def products():
    """Display all products with search functionality"""
    search_query = request.args.get('search', '')
    
    if search_query:
        products = Product.query.filter(
            (Product.code.ilike(f'%{search_query}%')) |
            (Product.name.ilike(f'%{search_query}%')) |
            (Product.location.ilike(f'%{search_query}%'))
        ).order_by(Product.name).all()
    else:
        products = Product.query.order_by(Product.name).all()
    
    return render_template('products.html', products=products, search_query=search_query)
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)