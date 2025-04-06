from flask_mail import Mail, Message
from flask import current_app

# Create the Mail instance globally
mail = Mail()

def send_reset_email(to, subject, body):
    msg = Message(subject, recipients=[to], sender=current_app.config['MAIL_DEFAULT_SENDER'])
    msg.body = body
    with current_app.app_context():
        mail.send(msg)
from flask_mail import Mail, Message
from flask import current_app


