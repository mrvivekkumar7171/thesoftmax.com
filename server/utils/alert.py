from email.message import EmailMessage
from dotenv import load_dotenv
import smtplib, os, random
load_dotenv()

SENDER_USER = os.getenv("SENDER_USER")
PASSWORD = os.getenv("PASSWORD")

def generate_otp():
    otp = f"{random.randint(100000, 999999):06d}"
    return otp

def send_otp(subject,otp,to_mail):
    # Plain text version (fallback)
    plain_text = f"""Hello,

Your One-Time Password (OTP) for verification on TheSoftMax.com is:

{otp}

This OTP is valid for 5 minutes. Do not share it with anyone.

If you did not request this, please ignore this email.

Thank you,
TheSoftMax Team
"""
    
    # HTML version with improved styling
    html_text = f"""\
    <html>
    <head>
        <style>
            .custom-bg{{
                color: #131417 !important;
            }}
            .custom-bg1{{
                color: #252830 !important;
            }}
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                max-width: 400px;
                margin: auto;
            }}
            .otp {{
                font-size: 24px;
                font-weight: bold;
                background: #007bff;
                padding: 15px 30px;
                display: inline-block;
                border-radius: 5px;
                margin: 20px 0;
                color: white;
            }}
            p {{
                font-size: 16px;
            }}
            .footer {{
                font-size: 14px;
                margin-top: 20px;
            }}
            a {{
                color: #007bff;
                text-decoration: none;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>OTP Verification</h1>
            <p>Your One-Time Password (OTP) for verification on  
            <a href="https://thesoftmax.com/">TheSoftMax.com</a> is:</p>
            <div class="otp">{otp}</div>
            <p>This OTP is valid for <strong>5 minutes</strong>. Do not share it with anyone.</p>
            <p>If you did not request this, please ignore this email.</p>
            <div class="footer">
                Thank you,<br>
                <strong>TheSoftMax Team</strong>
            </div>
        </div>
    </body>
    </html>
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = SENDER_USER
    msg["To"] = to_mail

    # Add both plain text and HTML content
    msg.set_content(plain_text)  # Fallback for non-HTML email clients
    msg.add_alternative(html_text, subtype="html")  # HTML version

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_USER, PASSWORD)
        server.send_message(msg)
        server.quit()

def new_user_added(email_to:str,email:str,name:str):
    """
    Send an alert to the admin to approve the user (show email and name of the user) as soon as a new user registers.
    """
        # Plain text version (fallback)
    plain_text = f"""New User Approval Required,

A new user has registered on TheSoftMax.com and requires approval.

Name: {name}
Email: {email}

Please review and approve the user at your earliest convenience.

Thank you,
TheSoftMax Team
"""
    
    # HTML version with improved styling
    html_text = f"""\
    <html>
    <head>
        <style>
            .custom-bg{{
                color: #131417 !important;
            }}
            .custom-bg1{{
                color: #15c !important;
            }}
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                text-align: center;
                font-size: 16px;
            }}
            .container {{
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                max-width: 400px;
                margin: auto;
            }}
            .details {{
                font-size: 18px;
                font-weight: bold;
                margin: 10px 0;
            }}
            p {{
                font-size: 16px;
            }}
            .footer {{
                font-size: 14px;
                margin-top: 20px;
            }}
            a {{
                text-decoration: none;
                font-weight: bold;
            }}
        </style>
    </head>
    <body class="custom-bg">
        <div class="container">
            <h1 class="custom-bg">New User Approval Required</h1>
            <p>A new user has registered on  
            <a href="https://thesoftmax.com/" class="custom-bg custom-bg1">TheSoftMax.com</a> and requires approval.</p>
            <p class="details custom-bg">Name: <span class="custom-bg1">{name}</span> <br> Email: <span class="custom-bg1">{email}</span></p>
            <p>Please review and approve the user at your earliest convenience.</p>
            <div class="footer">
                Thank you,<br>
                <strong class="custom-bg">TheSoftMax Team</strong>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["Subject"] = "New User Approval - TheSoftMax"
    msg["From"] = SENDER_USER
    msg["To"] = email_to

    # Add both plain text and HTML content
    msg.set_content(plain_text)  # Fallback for non-HTML email clients
    msg.add_alternative(html_text, subtype="html")  # HTML version

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SENDER_USER, PASSWORD)
        server.send_message(msg)
        server.quit()

if __name__ == '__main__':
    otp = generate_otp()
    # send_otp("OTP Verification - TheSoftMax",otp,"mrvivekkumar7171@gmail.com")
    new_user_added("mrvivekkumar7171@gmail.com","salmanqwer644@gmail.com","Vivek Kumar")