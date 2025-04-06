 @app.route('/history')
# @login_required
# def history():
#     id = session.get('user')
#     deets = db.session.query(Userupload).filter_by(upload_user_id=id).all()
#     payment = db.session.query(Payment).filter_by(payment_user_id=id).all()
#     userdeets = db.session.query(User).get_or_404(id)
#     return render_template('users/history.html',userdeets=userdeets,payment=payment,deets=deets)




# @app.route('/landing')
# @login_required
# def landing():
#     refno = session.get('trxno')
#     transaction_deets = db.session.query(Payment).filter(Payment.refno==refno).first()
#     #make a curl request to paystack end point 
#     url="https://api.paystack.co/transaction/verify/"+transaction_deets.refno
#     headers ={"Content_Type=":"application/json", "Authorization": "Bearer sk_test_9dbe896dcfd3742799aee38bb6d3df0278efe249"}
#     response =  requests.get(url,headers=headers)
#     rspjson = json.loads(response.text)
#     if rspjson['status']== True:
#         paystatus =rspjson['data']['gateway_response']
#         transaction_deets.payment_status='Pending'
#         db.session.commit()
#         return redirect(url_for('history'))
#     else:
#         flash("payment failed")
#         return redirect('/reports')#dsiplay all the payment reports










# @app.route('/intializ/paystack')
# @login_required
# def intialize_paystack():
#     deets =User.query.get(session['user'])
#     #make a curl rewuest to the pay
#     refno = session.get('trxno')
#     transaction_deets = db.session.query(Payment).filter(Payment.refno==refno).first()
#     #make a curl request to paystack end point 
#     url="https://api.paystack.co/transaction/initialize"
#     headers ={"content_type=":"Content-Type: application/json", "Authorization": "Bearer sk_test_9dbe896dcfd3742799aee38bb6d3df0278efe249"}
#     data={"email": deets.user_email,"amount": transaction_deets.payment_amt,"reference":refno}
#     response =  requests.post(url,headers=headers,data=json.dumps(data))
#     rspjson =response.json()
#     if rspjson['status']==True:
#         redirectURL= rspjson['data']['authorization_url']
#         return redirect(redirectURL)
#     else:
#         flash(" Please complete the form again")
#         return redirect('/dashboard')


# @app.route('/payment/<di>', methods=['GET', 'POST'])
# def payment(di):
#     if request.method == 'GET':
#         id= session.get('user')
#         userdeets = db.session.query(User).get_or_404(id)
#         deets= db.session.query(Userupload).filter_by(upload_id=di).first()

#         # deets = db.session.query(User).get(session['user'])
#         return render_template("users/payment.html", userdeets=userdeets,deets=deets)
#     elif request.method == 'POST':
#         amt = float(request.form.get('amount'))*100
#         user = request.form.get('fullname')
#         email = request.form.get('email')
#         # Generate a transaction reference for this transaction
#         ref = "LF" + str(generate_string(10))
#         # Insert into the database
#         payment = Payment(payment_amt=amt, payment_user_id=session['user'], payment_status='pending',ptupload=di,refno=ref)
#         db.session.add(payment)
#         db.session.commit()
#         # Save the reference no in session
#         session['trxno'] = ref
#         # Redirect to a confirmation page
#         return redirect('/payment_confirmation/')
#     else:
#         deets=db.session.query(User).get(session['userloggedin'])
#         return render_template("user/payment.html",userdeets=userdeets)

@app.route('/post_comment/',methods=['POST'])
@login_required
def post_comment():
    content = request.form.get("content")
    userid = session['user']
    bookid = request.form.get("uploadid")
    query = Usercomment(user_comment=content,comment_user_id=userid,comment_upload_id=bookid)
    db.session.add(query)
    db.session.commit()

    retstr = f"""<article class="blog-post">
        <h5 class="blog-post-title"></h5>
        <p class="blog-post-meta">Commented by me <a href="#"></a></p>

        <p>{content}</p>
        <hr> 
      </article>"""
    return retstr


@app.route('/project_details/<di>')
@login_required
def project_details(di):
    id = session.get('user')
    comments= db.session.query(Usercomment).filter_by(comment_upload_id=di).all()
    deets= db.session.query(Userupload).filter_by(upload_id=di).first()
    userdeets = db.session.query(User).get_or_404(id)
    return render_template('users/profile_details.html',userdeets=userdeets,deets=deets,comments=comments)





@login_required
def changepass():
    changep = ChangePass()
    id = session.get('user')
    userdeets = db.session.query(User).get_or_404(id)
    if request.method =="GET":
        return render_template('users/changedp.html',userdeets=userdeets,changep=changep)
    else:
        email= request.form.get('email')
        pwd = request.form.get('pwd')
        freshpwd = request.form.get('newpwd')
        chpwd=generate_password_hash(freshpwd)
        deets = db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd =deets.user_password
            if check_password_hash(hashed_pwd,pwd)==True:
                deets.user_password = chpwd
                db.session.commit()
                flash('your password have been changed Successfully',category='changeperror')
                return redirect(url_for('profile_view'))
            else:
                return render_template('users/changedp.html',userdeets=userdeets,changep=changep)
        else:
            flash('Check your email',category='changeperror')
            return render_template('users/changedp.html',userdeets=userdeets,changep=changep)
        




@app.route('/editprofile',methods=['POST','GET'])
@login_required
def editprofile():
    id = session.get("user")
    userdeets = db.session.query(User).get_or_404(id)
    edit = ProfileForm()
    if request.method=="GET":
        return render_template('users/edit_profile.html',userdeets=userdeets,edit=edit)
    else:
        if edit.validate_on_submit:
            fullname = request.form.get('fullname')
            lastname = request.form.get('lastname') 
            phone = request.form.get('phone')
            city = request.form.get('city')
            usertype = request.form.get('status')
            profile = request.form.get('profile')
            address =request.form.get('address')
            state = request.form.get('state')
            lga = request.form.get('lga')
            defpic= "default.png"
            filename = defpic
            pix =request.files.get('dp')
            filename =pix.filename
            pix.save(app.config['USER_PROFILE_PATH']+filename)
            userdeets.user_pix =filename
            userdeets.user_fname=fullname
            userdeets.user_lname=lastname
            userdeets.user_phone=phone
            userdeets.user_city=city
            userdeets.user_usertype=usertype
            userdeets.user_add= address
            userdeets.user_profile= profile
            userdeets.user_state=state
            userdeets.user_lga=lga
            db.session.commit()
            flash('your profile has been updated',category='profilemsg')
            return redirect(url_for('profile_view'))
        else:
            return render_template('users/edit_profile.html',edit=edit,userdeets=userdeets)
        




# @app.route("/login",methods=["POST","GET"])
# def login():
#     if request.method =="GET":
#         return render_template('users/login.html')
#     else:
#         email = request.form.get('email')
#         pwd =request.form.get('pwd')
#         deets = db.session.query(User).filter(User.user_email==email).first()
#         if deets != None:
#             hashed_pwd=deets.user_password
#             if check_password_hash(hashed_pwd,pwd)==True:
#                 session['user']=deets.user_id
#                 return redirect('/dashboard')
#             else:
#                 flash('invalid credentials, try again',category='error')
#                 return redirect('/login')
#         else:
#             flash('invalid Credentials, try again',category='error')
#             return redirect('/login')
    
    # def login():
    # if request.method =="GET":
    #     return render_template('user/loginpage.html')
    # else:
    #     email = request.form.get('email')
    #     pwd =request.form.get('pwd')
    #     deets = db.session.query(User).filter(User.user_email==email).first()
    #     if deets != None:
    #         hashed_pwd =deets.user_pwd

    #         if check_password_hash(hashed_pwd,pwd)==True:
    #             session['userloggedin']=deets.user_id

    #             return redirect('/dashboard')
    #         else:
    #             flash('invalid credentials, try again')
    #             return redirect('/login')
    #     else:
    #         flash('invalid Credentials, try again')
    #         return redirect('/login')











    
# @app.route("/dashboard")
# @login_required
# def dashboard():
#     id = session.get('user')
#     upload = db.session.query(Userupload).filter(Userupload.upload_user_id!=id).limit(3)
#     users = db.session.query(User). filter(User.user_id!=id).limit(3)
#     userdeets =db.session.query(User).get_or_404(id)
#     return render_template("users/dashboard.html",userdeets=userdeets,users=users,upload=upload)
        





# @app.route("/register",methods=["POST","GET"])
# def register():
#     reg=NewForm()
#     if request.method =="GET":
#         flash("you need to fill out all information")
#         return render_template("users/register.html",reg=reg)
#     else:
#         if reg.validate_on_submit():
#             fname = request.form.get("fname")
#             return "you have been registered"
#         else:
#             return render_template("users/register.html",reg=reg)
    