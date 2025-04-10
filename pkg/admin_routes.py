import random,string,os
import json,requests
from functools import wraps

from flask import render_template,request,abort,redirect,flash,make_response,session,url_for,jsonify
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash, check_password_hash
# Upload of a new project
from werkzeug.utils import secure_filename



from pkg import app,csrf
from pkg.models import db,Adminreg, Transaction, Product 
from pkg.forms import *





#This is a decoratoer to help check if there is a user logged in
def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('admin') !=None:
            return f(*args,**kwargs)
        else:
            flash('Access Denied')
            flash('You must be logged in first')
            return redirect('/admin/')
    return login_check



@app.route("/admin/", methods=["POST", "GET"])
def admin():
    if request.method == "GET":
        return render_template('admin/adminlog.html')
    else:
        username = request.form.get('email')
        pwd = request.form.get('pwd')
        
        deets = db.session.query(Adminreg).filter(Adminreg.admin_username == username).first()
        
        if deets != None:
            hashed_pwd = deets.admin_pwd

            if check_password_hash(hashed_pwd, pwd) == True:
                session['admin'] = deets.admin_id
                return redirect(url_for('all_users'))
            else:
                flash('Invalid credentials, try again', category='danger')
                return redirect('/admin/')
        else:
            flash('Invalid credentials, try again', category='danger')
            return redirect('/admin/')

@app.route('/orders')
@login_required
def orders():
    admin_id = session.get('admin')
    admindeets = db.session.query(Adminreg).get_or_404(admin_id)

    # Only fetch confirmed transactions
    confirmed_transactions = db.session.query(Transaction).filter(Transaction.status == 'confirmed').all()

    return render_template('admin/orders.html', transaction=confirmed_transactions, admindeets=admindeets)



@app.route('/all_users/')
@login_required
def all_users():
    id = session.get('admin')
    admindeets = db.session.query(Adminreg).get_or_404(id)
    deet = db.session.query(Product).all()
    
    return render_template('admin/all_user.html',deet=deet,admindeets=admindeets)








@app.route("/All_transactions")
@login_required
def all_transaction():
    id = session.get('admin')
    admindeets = db.session.query(Adminreg).get_or_404(id)
    userdeets = db.session.query(Transaction).all()
    return render_template('admin/transactions.html',admindeets=admindeets ,userdeets=userdeets)
 


@app.route("/shipment_confirmation/<int:di>/")
def payment_confirm(di):
    # Query the transaction by ID
    transaction = db.session.query(Transaction).filter_by(id=di).first()  # Use .first() to get the transaction

    if transaction:  # Check if the transaction exists
        transaction.shipment_status = 'shipped'  # Update shipment status
        db.session.commit()
        flash('Product shipped', category='paymentmsg')
    else:
        flash('Transaction not found', category='danger')

    return redirect(url_for('orders'))  # Redirect to the orders page



@app.route("/Product/<int:di>/")
def product_confirm(di):
    # Query the transaction by ID
    transaction = db.session.query(Transaction).filter_by(id=di).first()  # Use .first() to get the transaction

    if transaction:  # Check if the transaction exists
        transaction.status = 'confirmed'  # Update shipment status
        db.session.commit()
        flash('payment confirmed', category='paymentmsg')
    else:
        flash('Transaction not found', category='danger')

    return redirect(url_for('orders'))  # Redirect to the 






# @app.route('/edit_balance/<di>', methods=['POST', 'GET'])
# @login_required
# def edit_balance(di):
#     user = db.session.query(User).filter_by(user_id=di).first()  # Ensure 'first()' is used to get a single result

#     if request.method == 'POST':
#         btc_balance = request.form.get('btcbalance')
#         eth_balance = request.form.get('ethbalance')
#         freezed_balance = request.form.get('freezed')

#         if user:
#             user.btc_balance = btc_balance
#             user.eth_balance = eth_balance
#             user.freezed_balance = freezed_balance
#             db.session.commit()
#             flash('Balance updated successfully', category='success')
#         else:
#             flash('User not found', category='error')

#         return redirect(url_for('edit_all_user'))

#     # Render template with 'user' (this will work whether 'POST' is submitted or not)
#     return render_template('admin/editbalance.html', user=user)




  
    
    





# @app.route("/admin/delete/<id>/" ,methods=['POST','GET'])
# def all_delete(id):
#     payment = db.session.query).get_or_404(id)
   
#     transaction =db.session.query(Transaction).filter_by(trans_user_id=id)
#     db.session.delete(payment)
   
#     db.session.commit()
#     flash('payments has been deleted Successfully',category='paymentmsg')
#     return redirect(url_for('all_users'))


@app.route("/admin/confirm/<id>/")
def payment_confirmed(id):
    transaction =db.session.query(Transaction).get_or_404(id)
    transaction.status='Confirmed'
    db.session.commit()
    flash('Payment has been successfully confirmed',category='success')
    return redirect(url_for('all_transaction'))



@app.route("/admin/logout")
def admin_logout():
    if session.get('admin')!= None:
        session.pop('admin',None)
        flash('you\'ve logged out successfully',"success")
    return redirect(url_for('admin'))





@app.route('/upload_product/',  methods=['GET', 'POST'])
@login_required
def upload():
    id = session.get('admin')
    admindeets = db.session.query(Adminreg).get_or_404(id)
    deet = db.session.query(Product).all()
    if request.method == "GET":
      return render_template('admin/addproduct.html',deet=deet,admindeets=admindeets)
    else:
        allowed=['jpg','png']
        filesobj=request.files['project_image']
        filename=filesobj.filename
        newname='Default.png'
        #validation
        if filename=='':
            flash('Please Choose project',category='error')
        else:                
            pieces=filename.split('.')
            ext=pieces[-1].lower()
            if ext in allowed:
                newname=str(int(random.random()*10000000))+filename
                filesobj.save('pkg/static/uploads/'+ newname)
            else:
                flash("Not Allowed, File Type Must Be ['jpg','png'], File was not uploades",category='error')
        newfile=newname
        desc=request.form.get('desc')
        price =request.form.get('price')
        name =request.form.get('name')
        uploader = Product(price=price,name=name, desc=desc ,filename=newfile)
        db.session.add(uploader)
        db.session.commit()
        return redirect(url_for('all_users'))
            
    
# delete Product

@app.route('/delete_product/<int:id>')
def delete_product(id):
    # Find the product by ID
    product = Product.query.get_or_404(id)
    
    try:
        db.session.delete(product)  # Delete the product from the session
        db.session.commit()  # Commit the transaction to the database
        flash(f'Product {product.name} has been deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()  # Rollback if there's an error
        flash(f'Error: {str(e)}', 'danger')

    return redirect(url_for('all_users'))  
  



@app.route("/notifications")
@login_required
def notifications():
    # Query for all transactions that are in 'pending' status
    new_orders = Transaction.query.filter_by(status='pending').all()

    # Prepare the data to return to the front end
    notifications = []
    for order in new_orders:
        notifications.append({
            'id': order.id,
            'name': order.name,
            'email': order.email,
            'amount': order.amount,
            'timestamp': order.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'product_names': order.product_names,
        })

    return jsonify(notifications)
