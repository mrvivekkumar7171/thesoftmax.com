# To install the required packages: pip install -r requirements.txt
# To run the program: python app.py
from flask import Flask, flash, render_template, request, redirect, session, url_for, jsonify
import os, pyotp, uuid, glob, time, atexit, hmac, hashlib, razorpay
from authlib.integrations.flask_client import OAuth
from datetime import datetime, timedelta, timezone
from utils.alert import generate_otp, send_otp
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from utils.database import Database, db
from utils.payment import generateCode
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
from utils import satya
from random import *
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend before importing pyplot



load_dotenv()
MODE = os.getenv('MODE')
if MODE == "TEST":
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID_TEST')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET_TEST')
else:
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
flask_port = int(os.getenv("FLASK_PORT", 8000))
admin_auth_code = os.getenv("ADMIN_AUTH_CODE")
PEPPER = os.getenv("PASSWORD_PEPPER")
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    secret_key = uuid.uuid4().hex
    with open(".env", "a") as f:  # Append to .env file
        f.write(f"\nSECRET_KEY={secret_key}")
app = Flask(__name__)
app.config["SECRET_KEY"]=secret_key
app.config['SQLALCHEMY_DATABASE_URI']="sqlite:///database.db" # "sqlite:///ums.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=True
app.config["SESSION_TYPE"]='filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30) # logs users out after 30 days of inactivity
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevents JavaScript access
app.config['SESSION_COOKIE_SECURE'] = False # True # Ensures cookies are only sent over HTTPS.
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Protects against CSRF attacks
CORS(app, supports_credentials=True, origins=[os.getenv("DOMAIN_URL")])
db.init_app(app)
db_obj = Database()
bcrypt=Bcrypt(app)
csrf = CSRFProtect(app)
Session(app) # to store the session data at the server side instead of client side. # Initialize session
oauth = OAuth(app)
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
with app.app_context(): # Register the Google OAuth client within the Flask app context
    oauth.register("myApp",# Name of the OAuth client
                    client_id = os.getenv("OAUTH2_CLIENT_ID"), # Get OAuth client ID from environment variables
                    client_secret=os.getenv("OAUTH2_CLIENT_SECRET"), # Get OAuth client secret
                    server_metadata_url=os.getenv("OAUTH2_META_URL"), # OAuth metadata URL (Google OAuth endpoint)
                    #  access_token_url='https://oauth2.googleapis.com/token',
                    authorize_url='https://accounts.google.com/o/oauth2/auth',
                    # api_base_url='https://www.googleapis.com/oauth2/v1/',
                    client_kwargs={"scope": "openid profile email"}# Request access to basic profile information and email only
                    )


def validate_fields(*fields):
    return all(field.strip() for field in fields)

def clear_expired_sessions(path='flask_session'): 
    now = time.time() 
    lifetime = app.permanent_session_lifetime.total_seconds()

    for session_file in glob.glob(os.path.join(path, '*')): 
        if os.stat(session_file).st_mtime < now - lifetime: 
            os.remove(session_file)

@atexit.register
def cleanup_sessions():
    clear_expired_sessions('flask_session')

@app.before_request # Every time the user loads any page, Flask marks the session as "modified". The expiration clock resets to another 30 days. So if they visit on day 20, they stay logged in until day 50.
def extend_session_if_active():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=30)

    if 'user_id' or 'admin_id' in session:
        session.modified = True

def add_pepper(password: str) -> str:
    """
    Returns SHA256(password + secret pepper) in hex form.
    """
    return hmac.new(PEPPER.encode(), password.encode(), hashlib.sha256).hexdigest()



@app.route('/', methods=["GET"])
def home():
    return redirect('/user/')


# -------------------------ADMIN----------------------------
@app.route('/admin/', methods=["POST", "GET"])
@app.route('/admin/index', methods=["POST", "GET"])
@app.route('/admin/home', methods=["POST", "GET"])
def admin(): # delete otp if admin is sucessfully logged in.
    
    if session.get('admin_id'): # if admin is logged in then redirect to admin dashboard
        return redirect('/admin/dashboard')

    if session.get('user_id'): # to make sure and admin cannot login at same time.
        return redirect('/user/dashboard')

    if request.method == 'POST':
        admin_name = request.form.get('admin_name') # get the value of field if the request is post
        plain_password = request.form.get('admin_password')
        otp = request.form.get('otp')
        action = request.form.get('action')
        visitorId = request.form.get("visitorId")
        
        current_time = datetime.now(timezone.utc)

        if not validate_fields(admin_name,  plain_password): # check the value is not empty
            flash('Please fill all the field','danger')
            return jsonify({"error": "Please fill in all fields."}), 400
        
        admin = db_obj.get_admin_by_username(admin_name=admin_name) # fetch admin details from database by username
        if not admin:
            return jsonify({"error": "Admin not found. Please check your username."}), 400
        
        otp_attempts = db_obj.load_otp_attempt(admin.admin_email) # generating otp and validating it.
        if action == "generate_otp":
            if otp_attempts and otp_attempts.last_attempt:
                last_attempt_time = otp_attempts.last_attempt # Ensure last_attempt_time is also timezone-aware
                if last_attempt_time.tzinfo is None or last_attempt_time.tzinfo.utcoffset(last_attempt_time) is None:
                    last_attempt_time = last_attempt_time.replace(tzinfo=timezone.utc)
                
                if (current_time - last_attempt_time < timedelta(hours=24)) and otp_attempts.tries >= 5: # Check if OTP attempts are within limit (5 attempts in 24 hours)
                    return jsonify({"error": "Too many OTP requests. Try again after 24 hours."}), 400
            
            otp_code = generate_otp() # Generate OTP and send OTP email
            send_otp("OTP Verification - TheSoftMax", otp_code, admin.admin_email)
            peppered_password = add_pepper(plain_password)
            hashed_password = bcrypt.generate_password_hash(peppered_password, rounds=12).decode('utf-8')
            
            if otp_attempts: # Update or create OTP attempt record
                otp_attempts.otp = otp_code
                otp_attempts.tries += 1
                db_obj.save_otp_attempt(admin_name, admin.admin_email, hashed_password, otp_code, otp_attempts.tries)
            else:
                db_obj.save_otp_attempt(admin_name, admin.admin_email, hashed_password, otp_code, 1)
            return jsonify({"success": "OTP sent successfully to your registered email!"}), 200

        elif action == "validate_otp": # Validate OTP entered by admin
            if not otp_attempts or otp_attempts.otp == "000000":
                return jsonify({"error": "Please request an OTP first."}), 400
            last_try_time = datetime.fromisoformat(str(otp_attempts.last_attempt))
            if last_try_time.tzinfo is None:
                last_try_time = last_try_time.replace(tzinfo=timezone.utc)
            if current_time - last_try_time > timedelta(minutes=5):
                return jsonify({"error": f"OTP expired. Generate new OTP."}), 400
            
            peppered_password = add_pepper(plain_password)
            if (otp == otp_attempts.otp) and bcrypt.check_password_hash(admin.admin_password, peppered_password): # Successful admin login, create session
                
                if visitorId:
                    db_obj.update_admin_device(admin.admin_id, visitorId) # replace with (API verification)
                
                session['admin_id'] = admin.admin_id
                session['admin_name'] = admin.admin_name
                session['admin_email'] = admin.admin_email
                flash('Login Successfully!', 'success')
                return jsonify({"success": "OTP Validation Successfully! Redirecting to dashboard...", "redirect": "/admin/dashboard"}), 200
            else:
                return jsonify({"error": f"Invalid OTP or Password. {5 - otp_attempts.tries} tries left."}), 400
    
    return render_template('admin/index.html', title="Admin Login") # render the admin login page if the request is get

@app.route('/admin/dashboard')
def adminDashboard():

    if not session.get('admin_id'): # if admin is not logged in
        return redirect('/admin/')
    
    totalUsers, totalApprove, NotTotalApprove = db_obj.get_user_db_stat() # get user statistics from database.

    return render_template('admin/dashboard.html', title = "Admin Dashboard", totalUsers = totalUsers, totalApprove = totalApprove, NotTotalApprove=NotTotalApprove)

@app.route('/admin/sentiment-analyzer')
def adminSentimentAnalyzer():

    if not session.get('admin_id'):
        return redirect('/admin/')
    
    return render_template('admin/sentiment-analyzer.html',title="Sentiment Analyzer")

@app.route('/admin/manage-users', methods=["POST","GET"])
def adminGetAllUser():

    if not session.get('admin_id'): # if admin is not logged in
        return redirect('/admin/')
    
    if request.method == "POST":
        search_term = request.form.get('search')

        if search_term == '':
            flash('Please enter search term','warning')
        
        users = db_obj.search_users_by_name_or_email_or_id(search_term)
    else:
        users = db_obj.get_all_users()
    totalUsers, totalApprove, NotTotalApprove = db_obj.get_user_db_stat()
    
    return render_template('admin/manage-users.html', title = 'Manage Users', users = users, totalUsers = totalUsers, totalApprove = totalApprove, NotTotalApprove = NotTotalApprove)

@app.route('/admin/approve-user/<int:user_id>')
def adminApprove(user_id):

    if not session.get('admin_id'):
        return redirect('/admin/')

    user = db_obj.admin_approve_user(user_id, session['admin_id'], session['admin_email'], session['admin_name'])
    if user:
        flash(f'Successfully Approve {user.user_name}','success')
    return redirect('/admin/manage-users')

@app.route('/admin/disapprove-user/<int:user_id>')
def adminDisapprove(user_id):

    if not session.get('admin_id'):
        return redirect('/admin/')

    user = db_obj.admin_disapprove_user(user_id, session['admin_id'], session['admin_email'], session['admin_name'])
    if user:
        flash(f'Successfully Disapproved {user.user_name}','success')
    return redirect('/admin/manage-users')

@app.route('/admin/change-password',methods=["POST","GET"])
def adminChangePassword():

    if not session.get('admin_id'): # if admin is not logged in
        return redirect('/admin/')

    admin = db_obj.get_admin_by_email(admin_email=session['admin_email']) # fetch admin details from database.

    if request.method == 'POST':
        admin_name = request.form.get('admin_name')
        plain_password = request.form.get('admin_password')

        if not validate_fields(admin_name, plain_password): # check if the fields are valid or not.
            flash('Please fill the fields !','danger')
            return redirect('/admin/change-password')
        
        if admin.admin_name == admin_name: # if admin_name is same as session admin_name then update the password.
            peppered_password = add_pepper(plain_password)
            hashed_password = bcrypt.generate_password_hash(peppered_password, rounds=12).decode('utf-8')  # Ensure decoding
            db_obj.update_admin_credentials(session['admin_email'], hashed_password)
            flash('Password Update successfully !','success')
        else:
            flash('Invalid Username !', 'danger')
        return redirect('/admin/change-password')
    
    return render_template('admin/change-password.html', title='Change Password', admin=admin) # change password get request page.
 
@app.route('/admin/logout')
def adminLogout():

    if not session.get('admin_id'): # if admin is not logged in
        return redirect('/admin/')
    
    session.clear()

    flash('Logged out successfully', 'success') # flash message to show logout success
    return redirect('/admin/')

@app.route('/admin/signup', methods=['GET', 'POST'])
def adminSignup():

    if request.method == 'POST': # fatching details from the form for signup if post request
        admin_name = request.form.get('admin_name')
        admin_email = request.form.get('admin_email')
        plain_password = request.form.get('admin_password')
        auth_totp = request.form.get('auth_code')
        action = request.form.get('action')
        current_time = datetime.now(timezone.utc)

        otp_attempts = db_obj.load_otp_attempt(admin_email) # loading the otp attempts
        otp = None
        peppered_password = add_pepper(plain_password)
        hashed_password = bcrypt.generate_password_hash(peppered_password, rounds=12).decode('utf-8') # generating password hash
        
        if not validate_fields(admin_name, admin_email, plain_password): # Validate input fields
            return jsonify({"error": "All fields are required."}), 400
        
        existing_admin = db_obj.cheking_existing_admin(admin_email, admin_name)
        if existing_admin:
            return jsonify({"error": "Username or Email already taken."}), 400
        
        if otp_attempts: # Check OTP attempt limits (Avoid spamming)
            last_try_time = datetime.fromisoformat(str(otp_attempts.last_attempt))
            if last_try_time.tzinfo is None:
                last_try_time = last_try_time.replace(tzinfo=timezone.utc)
            if (current_time - last_try_time < timedelta(hours=24) and otp_attempts.tries > 5):
                return jsonify({"error": "Too many failed attempts. Try again after 24 hours."}), 400
        else:
            db_obj.save_otp_attempt(admin_name,admin_email, hashed_password,"000000", 0)

        if action == "generate_otp": # Generate OTP
            otp = generate_otp()
            send_otp("OTP Verification - TheSoftMax", otp, admin_email)  
            otp_attempts = db_obj.load_otp_attempt(admin_email)
            otp_attempts.tries += 1
            db_obj.save_otp_attempt(admin_name, admin_email, hashed_password, otp, otp_attempts.tries)
            return jsonify({"success": "OTP sent successfully!"})

        elif action == "validate_otp": # Validate OTP by Convert auth_code to int and validate.
            try:
                auth_totp = int(auth_totp)
                totp = pyotp.TOTP(admin_auth_code)
                if not totp.verify(auth_totp): # replace the code with google auth code
                    return jsonify({"error": "Incorrect Admin Authentication Code."}), 400
            except ValueError:
                return jsonify({"error": "Invalid authentication code."}), 400
            
            entered_otp = request.form.get("mail_otp")
            if not otp_attempts or otp_attempts.otp == "000000": # Check if OTP request exists
                return jsonify({"error": "OTP is required./No OTP request found. Please generate OTP first."}), 400
        
        last_try_time = datetime.fromisoformat(str(otp_attempts.last_attempt))
        if last_try_time.tzinfo is None:
            last_try_time = last_try_time.replace(tzinfo=timezone.utc)
        if current_time - last_try_time > timedelta(minutes=5):
            return jsonify({"error": f"OTP expired. Generate new OTP."}), 400
        
        if entered_otp == otp_attempts.otp: # store Hash password and admin details if entered otp and sent otp.
            db_obj.add_new_admin(admin_name=admin_name, admin_email=admin_email, hashed_password=hashed_password)
            flash('Admin registered successfully! Please login.','success')
            return jsonify({"success": "Admin registered successfully!", "redirect": "/admin/"}), 200
        
        else: # notify invalid otp
            db_obj.save_otp_attempt(admin_name,admin_email, hashed_password, otp_attempts.otp, otp_attempts.tries)
            return jsonify({"error": f"Invalid OTP. {5 - otp_attempts.tries} tries left."}), 400
        
    return render_template('admin/signup.html', title='Admin Signup') # render signup page if get request.







# -------------------------USER----------------------------
@app.route('/user/', methods=["GET"])
@app.route('/user/home', methods=["GET"])
@app.route('/user/index', methods=["GET"])
def userIndex():

    if  session.get('user_id'):
        return redirect('/user/dashboard')
    
    if session.get('admin_id'):
        return redirect('/admin/dashboard')
    
    return render_template('user/index.html', title="User Login")

@app.route("/user/fingerprintJS", methods=["POST"])
@csrf.exempt
def storeFingerprint():
    data = request.get_json(silent=True) or {}
    session["visitorId"] = data.get("visitorId")
    return {"status": "ok"}

@app.route('/user/google_login') # Route to initiate Google login
def googleLogin():

    # Generate a redirect URL for Google authentication and send the user there
    redirect_uri = url_for("googleCallback", _external=True) # Generate an absolute URL for the callback

    return oauth.myApp.authorize_redirect(redirect_uri=redirect_uri)

@app.route('/user/signin_google') # Route for handling the OAuth callback from Google
def googleCallback():
    token = oauth.myApp.authorize_access_token() # Get the authentication token after successful login
    visitorId = session.pop("visitorId", None)  # 🔐 retrieve & delete

    user_email = token.get("userinfo", {}).get("email") # Extract user email from Google OAuth response
    user_name = token.get("userinfo", {}).get("name", "Unknown")  # Fallback to 'Unknown' if name is missing

    if user_email:  # Ensure email is retrieved
        existing_user = db_obj.get_user_by_email(user_email=user_email) # Check if user already exists in the database

        if not existing_user:  # If the user is new, add them to the database
            existing_user = db_obj.add_new_user(user_email=user_email, user_name=user_name)
            db_obj.notify_admins_of_new_user(user_email=user_email, user_name=user_name)
            
            flash("Your account is created but requires admin approval. Please wait for next 24 hours!", "warning")
            return redirect('/user/')

        if existing_user.user_status == 0:
            flash("Your account is not approved by Admin. Please wait for next 24 hours!", "danger")
            return redirect('/user/')
        
        if visitorId:
            db_obj.update_user_device(existing_user.user_id, visitorId) # replace with (API verification)

        session['user_id'] = existing_user.user_id
        session['user_name'] = existing_user.user_name
        session['user_email'] = existing_user.user_email

        flash("Login Successful", "success")
        return redirect(request.args.get("next") or '/user/dashboard') # Redirect to the home page where user details will be displayed
    
    flash("Login failed. Please try again.", "danger")
    return redirect('/user/')

@app.route('/user/dashboard')
def userDashboard():

    if not session.get('user_id'):
        return redirect('/user/')
    
    user = db_obj.get_user_by_email(session['user_email'])

    return render_template('user/dashboard.html', title="User Dashboard", user=user)

@app.route('/user/sentiment-analyzer')
def userSentimentAnalyzer():

    if not session.get('user_id'):
        return redirect('/user/')
    
    user = db_obj.get_user_by_email(user_email=session['user_email'])

    return render_template('user/sentiment-analyzer.html', title="Sentiment Analyzer", user=user)

@app.route('/user/logout')
def userLogout():

    if session.get('user_id'):
        session.clear() # using this will clear all the session data including admin session if both admin and user are logged in.

        flash("Logged out successfully", "success")

    return redirect('/user/')

@app.route('/user/payment')
def payment():

    if not session.get('user_id'):
        return redirect('/user/')

    return render_template('/user/payment.html', key_id = RAZORPAY_KEY_ID)

@app.route('/user/payment/order', methods=['POST'])
def create_order():
    
    if not session.get('user_id'):
        return redirect('/user/')

    data = request.get_json(silent=True)

    amount = int(data["amount"]) * 100 # amount in paise

    try : 
        razorpay_order = razorpay_client.order.create(data={"amount": amount,"currency": 'INR'})

        try :
            r_status = db_obj.register_new_order(order_id=razorpay_order['id'], amount=razorpay_order['amount'], currency='INR', payment_status=razorpay_order['status'], user_id=session['user_id'], booking_type='TOKEN')
            if not r_status:
                flash('failed to register_new_order !','danger')
                return redirect('/user/payment')
        except Exception as e:
            flash('Error saving order id','danger')
            return redirect('/user/payment')

    except Exception as e:
        flash('Error encountered !','danger')
        return redirect('/user/payment')

    return jsonify({"order_id": razorpay_order['id'], "amount": amount})

@app.route('/user/payment/success')
def payment_success():

    if not session.get('user_id'):
        return redirect('/user/')

    return render_template("/user/success.html")

@app.route('/user/payment/verify', methods=['POST'])
@csrf.exempt
def verify_signature():

    if not session.get('user_id'):
        return redirect('/user/')

    # Data from Razorpay Checkout
    payment_id = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")

    try: # Verify signature
        razorpay_client.utility.verify_payment_signature({"razorpay_order_id": order_id, "razorpay_payment_id": payment_id, "razorpay_signature": signature})
        

        try :
            # If the order does not exist → reject.
            # If the order exists but is already paid (payment_id, order_id, signature, status is sucessfull)→ reject.
            c_status = db_obj.payment_status_completed(order_id=order_id, payment_id=payment_id, signature=signature, user_id=session['user_id'])
            if not c_status:
                flash('failed to register payment_status_completed !','danger')
                return redirect('/user/payment')
        except Exception as e:
            flash('Error while saving payment status','danger')
            return redirect('/user/payment')

        flash('Payment successful and credits added to your account.','success')
        return redirect('/user/payment/success')
    except razorpay.errors.SignatureVerificationError: # raises error
        
        try :
            f_status = db_obj.payment_status_failed(order_id=order_id, payment_id=payment_id, signature=signature, user_id=session['user_id'])
            if not f_status:
                flash('failed to register payment_status_failed !','danger')
                return redirect('/user/payment')
        except Exception as e:
            flash('Error while saving payment status','danger')
            return redirect('/user/payment')

        return "Signature verification failed", 400

@app.route('/user/payment/donate', methods=['GET', 'POST'])
def donate():

    if not session.get('user_id'):
        return redirect('/user/')
    
    generatedCode = ''
    if request.method == 'POST': # If the form is submitted  
        amount = str(request.form['amount']) # Get the input text
        if amount: # Check if the input text is not empty
            generatedCode = generateCode(amount=amount, note=str(session['user_id'])) # Generate the QR code
        else:
            flash("Please enter amount to generate code", "danger")
    
    # Render the HTML template and pass the QR code
    return render_template('/user/donate.html', generatedCode = generatedCode, title="Donate")




# ----------------------------------- Model 1 (Satya) ----------------------------------
@app.route('/api/health')
def health_check():

    if session.get('user_id'):
        return jsonify({"status": "ok", "logged_in": True, "user_id": session['user_id']})
    elif session.get('admin_id'):
        return jsonify({"status": "ok", "logged_in": True, "admin_id": session['admin_id']})
    return jsonify({"status": "not_logged_in", "logged_in": False}), 200

@csrf.exempt
@app.route('/api/generate_chart', methods=['POST'])
def generate_chart():
  
    if not session.get('user_id') and not session.get('admin_id'):
        return jsonify({"error": "User not logged in"}), 401
    
    response = satya.generate_chart(request)
    return response

@csrf.exempt                  
@app.route('/api/generate_wordcloud', methods=['POST'])
def generate_wordcloud():
    
    if not session.get('user_id') and not session.get('admin_id'):
        return jsonify({"error": "User not logged in"}), 401
    
    response = satya.generate_wordcloud(request)
    return response

@csrf.exempt
@app.route('/api/generate_trend_graph', methods=['POST'])
def generate_trend_graph():

    if not session.get('user_id') and not session.get('admin_id'):
        return jsonify({"error": "User not logged in"}), 401

    response = satya.generate_trend_graph(request)
    return response

@csrf.exempt
@app.route('/api/analyze_video', methods=['POST'])
def analyze_video():
    data = request.get_json()

    if session.get('user_id'):
        video_id = data.get('videoId')
        visitorId = data.get("visitorId")
        if not video_id or not visitorId:
            return jsonify({"error": "No Video ID or Visitor ID provided"}), 400
        if not db_obj.check_user_device(session['user_id'], visitorId):
            return jsonify({"error": "Request from unknown device"}), 400
        
    elif session.get('admin_id'):
        video_id = data.get('videoId')
        visitorId = data.get("visitorId")
        if not video_id or not visitorId:
            return jsonify({"error": "No Video ID or Visitor ID provided"}), 400
        if not db_obj.check_admin_device(session['admin_id'], visitorId):
            return jsonify({"error": "Request from unknown device"}), 400
        
    else:
        return jsonify({"error": "User not logged in"}), 401
    
    results = satya.analyze_youtube_video(video_id)
    if isinstance(results, dict) and "error" in results:
        return jsonify(results), 500
        
    return jsonify(results)

# ----------------------------------- Model 2 ----------------------------------

# ----------------------------------- Model 3 ----------------------------------




if __name__=="__main__":
    with app.app_context():
        db.create_all() # create the database if not created
    app.run(host='0.0.0.0', port=flask_port, debug=True) # debug=True is used to load pages on changes and only for development environment