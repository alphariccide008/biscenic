from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileRequired,FileAllowed
from wtforms import StringField, SubmitField, TextAreaField ,PasswordField,RadioField,validators
from wtforms.validators import Email, DataRequired, EqualTo, Length



class RegForm(FlaskForm):
    fname = StringField("FirstName",validators=[DataRequired(message="Input your First Name")])
    lname = StringField("Last Name",validators=[DataRequired(message="Input your Last Name")])
    email = StringField("Email",validators=[Email(),DataRequired(message="Input valid email")])
    ssn = StringField("Ssn",validators=[Email(),DataRequired(message="Input valid ssn")])
    address = StringField("Email",validators=[Email(),DataRequired(message="Input valid Address")])
    city = StringField("Email",validators=[Email(),DataRequired(message="Input valid city")])
    zipcode = StringField("Email",validators=[Email(),DataRequired(message="Input valid zipcode")])
    balance = StringField("Balance",validators=[Email(),DataRequired(message="Input balance ")])
    pwd = PasswordField("Enter Password",validators=[DataRequired(message="Password must match")])
    confpwd = PasswordField("Confirm Password",validators=[DataRequired(message="password don't match"),EqualTo("pwd")])
    btnsubmit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.Length(min=6, max=35),validators.Email()])
    password = PasswordField('New Password', [validators.DataRequired()])
    


class Uploadfile(FlaskForm):
        image = FileField("upload Project Image",validators=[FileAllowed(['jpg','png','jpeg'])])
        name = StringField("input name",validators=[DataRequired(message="Please Input A description")])
        amount= StringField("Project Price",validators=[DataRequired(message="Price")])
        action = StringField("Type of transaction",validators=[DataRequired(message="Price")])


class Withdrawal(FlaskForm):
        transplan = StringField("Type of transaction",validators=[DataRequired(message="Price")])
        name = StringField("input name",validators=[DataRequired(message="Please Input A description")])
        amount= StringField("Project Price",validators=[DataRequired(message="Price")])
        action = StringField("transactipn type",validators=[DataRequired(message="Price")])

class EditBalance(FlaskForm):
        btcbalance = FileField("Input btcbalance",validators=[FileAllowed(['jpg','png','jpeg'])])
        ethbalance = StringField("input Ethbalance",validators=[DataRequired(message="Please Input A description")])
        freezed= StringField("Inout Freezed Balance",validators=[DataRequired(message="Price")])
        

class TransForm(FlaskForm):
    amount = StringField("amount",validators=[DataRequired(message="Input amount")])
    transplan = StringField("plan",validators=[DataRequired(message="Select a plan")])
    transname = StringField("paymentname",validators=[Email(),DataRequired(message="Input valid email")])
    

