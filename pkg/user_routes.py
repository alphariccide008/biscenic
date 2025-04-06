import random,string
import json,requests, uuid
from functools import wraps

from flask import Blueprint,render_template,request,abort,redirect,flash,make_response,session,url_for,jsonify
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash


from pkg import app,csrf
from pkg.email_utils import send_reset_email 
from datetime import datetime,timedelta
import pytz
from pkg.models import db,User,Transaction, Product, CartItem
from pkg.forms import *
from itsdangerous import URLSafeTimedSerializer
from . import mail


from flask_mail import Message
import secrets  

user_routes = Blueprint('user_routes', __name__)
serializer = URLSafeTimedSerializer('your_secret_key')

def verify_token(token):
    try:
        # This assumes your tokens were generated using the serializer
        email = serializer.loads(token, max_age=3600)  # Token valid for 1 hour
        return email  # Return the email associated with the token
    except Exception as e:
        return None  # Token is invalid or expired
    

def generate_otp():
    return str(random.randint(100000, 999999))  # Generate OTP as a string




#This is a decoratoer to help check if there is a user logged in
def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('user')!=None:
            return f(*args,**kwargs)
        else:
            flash("Access denied ,Login", "danger")
            return redirect('/login')
    return login_check 


def generate_string(howmany):#call this function as renerate_string(10)
    x = random.sample(string.digits,howmany)
    return ''.join(x)


 





@app.before_request
def create_session_user():
    if 'user_id' not in session:
        session_id = str(uuid.uuid4())
        user = User(session_id=session_id)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id


@app.route("/")
def home():
    return render_template("users/index.html",title="Home")

app.route('/about')
def about():
    return ('')

@app.route("/all-product")
def all():
    products = Product.query.all()
    return render_template("index.html", products=products)

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):
    user_id = session.get('user_id')
    item = CartItem(user_id=user_id, product_id=product_id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    user_id = session.get('user_id')
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    total = sum(item.product.price for item in cart_items)
    return render_template("users/cart.html", items=cart_items, total=total)

@app.route("/pay", methods=["POST"])
def pay():
    user_id = session.get('user_id')
    email = request.form["email"]
    user = User.query.get(user_id)
    user.email = email
    db.session.commit()

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    amount = sum(item.product.price for item in cart_items) * 100

    headers = {
        "Authorization": "Bearer YOUR_PAYSTACK_SECRET_KEY",
        "Content-Type": "application/json"
    }

    data = {
        "email": email,
        "amount": amount,
        "callback_url": url_for("payment_callback", _external=True)
    }

    res = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    response_data = res.json()

    if res.status_code == 200 and response_data["status"]:
        reference = response_data["data"]["reference"]
        transaction = Transaction(user_id=user_id, amount=amount, status="pending", reference=reference)
        db.session.add(transaction)
        db.session.commit()
        return redirect(response_data["data"]["authorization_url"])
    else:
        return "Payment failed", 400

@app.route("/payment/callback")
def payment_callback():
    # Verify the payment here using Paystack API and update transaction status
    return "Payment successful!"







@app.errorhandler(404)
def error_page(errors):
    return render_template("users/errorpage.html")



@app.after_request
def after_request(response):
    response.headers["cache-control"]="no-cache, no-store, must-revalidate"
    return response











