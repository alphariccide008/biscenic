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
    return render_template("users/all.html", products=products)

@app.route("/viewproduct/<id>")
def viewall(id):
    products = db.session.query(Product).filter_by(id=id).first()
    return render_template("users/productdetails.html", products=products)






# tem. Add product


@app.route("/add-to-cart/<int:id>")
def add_to_cart(id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect if user is not logged in

    # Fetch the product from DB
    product = Product.query.get_or_404(id)

    # Check if the product already exists in the cart
    existing_item = CartItem.query.filter_by(user_id=user_id, product_id=id).first()

    if existing_item:
        # If the product is already in the cart, increment the quantity
        existing_item.quantity += 1
    else:
        # If the product doesn't exist in the cart, create a new cart item
        new_item = CartItem(
            user_id=user_id,
            product_id=id,
            name=product.name,
            filename=product.filename,  # Store the product's filename
            price=product.price,
            quantity=1  # Set initial quantity to 1
        )
        db.session.add(new_item)

    db.session.commit()  # Save changes to the database

    # Ensure that we are returning a valid response (redirecting to the cart page)
    return redirect(url_for('cart'))  # Redirect to cart page or a different page as needed





@app.context_processor
def inject_cart_count():
    user_id = session.get('user_id')
    count = CartItem.query.filter_by(user_id=user_id).count() if user_id else 0
    return dict(cart_count=count)


@app.route("/remove-from-cart/<int:item_id>")
def remove_from_cart(item_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect if user is not logged in
    
    # Fetch the cart item to be removed
    cart_item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    
    if cart_item:
        db.session.delete(cart_item)  # Delete the item from the database
        db.session.commit()  # Commit the changes to the database
    
    return redirect(url_for('cart'))  # Redirect back to the cart page



@app.route("/cart")
def cart():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user = User.query.get(user_id)  # Retrieve the logged-in user from the database
    cart_items = CartItem.query.filter_by(user_id=user_id).all()  # Get items in the cart for the logged-in user
    total = sum(item.product.price * item.quantity for item in cart_items)  # Calculate the total price

    return render_template('users/cart.html', items=cart_items, total=total, user=user)






@app.route("/pay", methods=["POST","GET"])
def pay():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('home'))  # If not logged in, redirect to login page
    
    # Get user and update their email
    email = request.form["email"]
    user = User.query.get(user_id)
    user.email = email  # Update email in the user table
    db.session.commit()
    
    # Get all cart items for the logged-in user
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for('cart'))  # Or wherever your cart page is
    
    # Calculate total amount
    amount = sum(item.product.price * item.quantity for item in cart_items) * 100  # Total amount in kobo (Paystack uses kobo)
    
    # Paystack headers and data for initializing transaction
    headers = {
        "Authorization": "Bearer sk_test_f3f650ddd241d9c89f13c3d9468162052fcc8152",  # Update with your own secret key
        "Content-Type": "application/json"
    }
    
    data = {
        "email": email,
        "amount": amount,
        "callback_url": url_for("payment_callback", _external=True)  # Callback URL after payment
    }
    
    try:
        res = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        response_data = res.json()
        
        if res.status_code == 200 and response_data["status"]:
            reference = response_data["data"]["reference"]
            
            # Save the transaction in the database with 'pending' status
            transaction = Transaction(user_id=user_id, amount=amount, status="pending", reference=reference)
            db.session.add(transaction)
            db.session.commit()
            
            return redirect(response_data["data"]["authorization_url"])  # Redirect to Paystack's payment page
        else:
            flash("Payment initialization failed: " + response_data.get("message", "Unknown error"), "danger")
            return redirect(url_for('checkout'))  # Adjust this to redirect to your checkout page or cart page
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('checkout'))  # Adjust this to redirect to your checkout page or cart page





@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # If not logged in, redirect to login page

    # Get all cart items for the logged-in user
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for('cart'))  # Or wherever your cart page is

    # Get the total amount
    total_amount = sum(item.product.price * item.quantity for item in cart_items) * 100  # In kobo (Paystack uses kobo)

    # Get address from the form
    address = request.form["address"]  # Ensure this field is in your form

    # Get product names to store in the transaction
    product_names = [item.product.name for item in cart_items]  # List of product names
    product_names_str = ", ".join(product_names)  # Convert list to comma-separated string

    # Create a new transaction in the database
    transaction = Transaction(
        user_id=user_id, 
        amount=total_amount, 
        status="pending",
        name=request.form["name"],  # Assuming name is sent from the form
        email=request.form["email"],  # Assuming email is sent from the form
        address=request.form["address"],  # Save address to the transaction
        filename="default-image.jpg",  # You can update this as needed
        product_names=product_names_str  # Save the product names as a comma-separated string
    )
    db.session.add(transaction)
    db.session.commit()

    # Clear the cart before proceeding to payment
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Initialize the Paystack payment request
    headers = {
        "Authorization": "Bearer sk_test_f3f650ddd241d9c89f13c3d9468162052fcc8152",  # Update with your secret key
        "Content-Type": "application/json"
    }

    # Construct the data for Paystack initialization
    data = {
        "email": request.form["email"],  # Get email from form
        "amount": total_amount,  # Paystack expects amount in kobo
        "callback_url": url_for("home", _external=True),  # Callback URL after payment
        "metadata": {"product_names": product_names_str}  # Include product names in metadata
    }

    try:
        res = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        response_data = res.json()

        if res.status_code == 200 and response_data["status"]:
            reference = response_data["data"]["reference"]

            # Update transaction with the reference from Paystack
            transaction.reference = reference
            db.session.commit()

            # Redirect to Paystack's payment page
            return redirect(response_data["data"]["authorization_url"])
        else:
            flash("Payment initialization failed: " + response_data.get("message", "Unknown error"), "danger")
            return redirect(url_for('cart'))  # Redirect back to the cart page if payment fails

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('cart'))  # Redirect back to cart if an error occurs
# Redirect back to cart if an error occurs








@app.errorhandler(404)
def error_page(errors):
    
    flash('Thanks for placing your Order','danger')
    return render_template("users/errorpage.html")



@app.after_request
def after_request(response):
    response.headers["cache-control"]="no-cache, no-store, must-revalidate"
    return response





# Temporary add product page



# @app.route('/addproduct',methods=['POST','GET'])
# def addporduct():
#     userdeets = db.session.query(Product).all()
#     if request.method == "GET":
#       return render_template("users/addproduct.html",userdeets=userdeets,uploadfile=uploadfile)
#     else:
#          if request.method =='GET':
#             deets= db.session.query(Product).all()
#             return render_template('users/uploadproject.html',deets=deets,userdeets=userdeets)
#          else:
#             #retrieve the file
#             allowed=['jpg','png']
#             filesobj=request.files['projectdp']
#             filename=filesobj.filename
#             newname='Default.png'
#             #validation
#             if filename=='':
#                 flash('Please Choose project',category='error')
#             else:                
#                 pieces=filename.split('.')
#                 ext=pieces[-1].lower()
#                 if ext in allowed:
#                     newname=str(int(random.random()*10000000))+filename
#                     filesobj.save('pkg/static/uploads/'+ newname)
#                 else:
#                     flash("Not Allowed, File Type Must Be ['jpg','png'], File was not uploades",category='error')
#             newfile=newname
#             desc=request.form.get('projectdescription')
#             price =request.form.get('projectprice')
#             uploader = Userupload(upload_amt=price, upload_desc=desc ,upload_filename=newfile,upload_user_id =id)
#             db.session.add(uploader)
#             db.session.commit()
#             return redirect(url_for('profile_view'))
            




