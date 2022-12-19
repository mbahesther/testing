from run import app, CORS
import os
import ssl
import smtplib
from flask import url_for
from email.message import EmailMessage

from flask_jwt_extended import ( JWTManager,create_access_token, get_jwt_identity,
                jwt_required, current_user)


jwt_manager = JWTManager(app)

def merchant_forgot_password(usermail):
        email_sender = 'omanovservices@gmail.com'
        email_password = os.getenv('EMAIL_PASSWORD')

        email_receiver = usermail
        subject = "Password Reset"
        access_token = create_access_token(identity=usermail)
        
        body = (f'''You request for a new password, click on the link to reset your password' {url_for('merchant_password_reset', token=access_token, _external=True)} 'If you did not make this request simply ignore''')
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

