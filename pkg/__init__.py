# pkg/__init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail  # Import Flask-Mail

# Instantiate CSRF and Mail objects
csrf = CSRFProtect()
mail = Mail()  # Create a Mail instance

def create_app():
    from pkg.models import db

    app = Flask(__name__)
    app.config.from_pyfile("config.py", silent=True)

    # Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update if using a different provider
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'goldcapitalfinance@gmail.com'  # Your email
    app.config['MAIL_PASSWORD'] = 'mcuh srmx ktve kphq'  # Your email password or app password
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@goldcapitalinvestment.pythonanywhere.com'  # Default sender email

    db.init_app(app)
    migrate = Migrate(app, db)
    csrf.init_app(app)

    # Initialize the Mail object with the app
    mail.init_app(app)

    return app

app = create_app()

# Load routes from here 
from pkg import admin_routes, user_routes
from pkg.forms import *
