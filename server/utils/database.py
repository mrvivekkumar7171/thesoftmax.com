from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from utils.alert import new_user_added
from decimal import Decimal
from enum import Enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    user_id=db.Column(db.Integer, primary_key=True, comment='Auto-incrementing ID')
    user_email=db.Column(db.String(255), unique=True, nullable=False)
    user_name=db.Column(db.String(255), nullable=False)
    user_status=db.Column(db.Integer,default=0, nullable=False)
    user_credits = db.Column(db.Numeric(10, 2), default=10.00, nullable=False)
    device_id = db.Column(db.String(255), nullable=True, comment="Device info of the user")

    # created_at TIMESTAMP CURRENT_TIMESTAMP When the user account was created
    # updated_at TIMESTAMP CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP When the user account was last updated

    def __repr__(self):
        return f'User("{self.user_id}","{self.user_email}","{self.user_name}","{self.user_status}")'

class Admin(db.Model):
    __tablename__ = "admin"
    admin_id=db.Column(db.Integer, primary_key=True)
    admin_name=db.Column(db.String(255), nullable=False, unique=True)
    admin_email = db.Column(db.String(255), nullable=False, unique=True)
    admin_password=db.Column(db.String(255), nullable=False)
    device_id = db.Column(db.String(255), nullable=True, comment="Device info of the user")

    def __repr__(self):
        return f'Admin("{self.admin_name}","{self.admin_email}")'

class newAdmin(db.Model):
    __tablename__ = "newadmin"
    admin_id=db.Column(db.Integer, primary_key=True)
    admin_name=db.Column(db.String(255), nullable=False, unique=True)
    admin_email = db.Column(db.String(255), nullable=False, unique=True)
    admin_password=db.Column(db.String(255), nullable=False)
    otp = db.Column(db.String(6), nullable=False)  # OTP (6-digit)
    tries = db.Column(db.Integer, default=0)  # Number of OTP attempts
    last_attempt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'Admin("{self.admin_name}","{self.admin_email}")'

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    ERROR = 'error'

class Payment(db.Model):
    __tablename__ = "payment"

    order_id = db.Column(db.String(255), primary_key=True, nullable=False, comment="Gateway order ID")
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False, comment="User who made the payment")
    booking_type = db.Column(db.String(50), nullable=False, comment="ID of the associated product like 'subscription', 'token', 'ebook', etc.") # make it FOREIGN KEY
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False, comment="When the payment was created")
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING, comment="Current status of the payment")
    amount = db.Column(db.Numeric(10), nullable=False, comment="Amount in paise")
    currency = db.Column(db.String(10), default="INR", nullable=False, comment="Currency of the payment, default is INR")
    signature = db.Column(db.String(255), nullable=True, comment="Gateway Signature for validation")
    paid_at = db.Column(db.DateTime, nullable=True, comment="When the payment was made successfully")
    failure_at = db.Column(db.DateTime, nullable=True, comment="When the payment failed")
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=True, comment="Payment method used")
    payment_id = db.Column(db.String(100), unique=True, comment="Unique payment reference from the gateway")

    user = db.relationship("User", backref="payment")

    def __repr__(self):
        return f'<Payment {self.payment_id} | {self.payment_status.value} | {self.amount} {self.currency}>'

    # Reviews Table
    # review_id INT PRIMARY KEY, AUTO_INCREMENT Unique identifier for each review
    # user_id INT NOT NULL, FOREIGN KEY (Users.user_id) ID of the reviewer
    # event_id INT NOT NULL, FOREIGN KEY (Events.event_id) ID of the reviewed event
    # rating TINYINT NOT NULL, CHECK (1-5) Star rating (1-5)
    # comment TEXT NULL Detailed review comments
    # created_at TIMESTAMP CURRENT_TIMESTAMP When the review was submitted

    #  Notifications Table
    # notification_id INT PRIMARY KEY, AUTO_INCREMENT Unique identifier for each notification
    # user_id INT NOT NULL, FOREIGN KEY (Users.user_id) Recipient user ID
    # message TEXT NOT NULL Notification content
    # notification_type ENUM('email', 'sms', 'app') NULL How the notification was sent
    # is_read BOOLEAN FALSE Whether notification was viewed
    # created_at TIMESTAMP CURRENT_TIMESTAMP When notification was created

class Database():

    def update_user_device(self, user_id, device_id):
        user = db.session.get(User, user_id)
        if user:
            user.device_id = device_id
            db.session.commit()
            return user
        return None
    
    def update_admin_device(self, admin_id, device_id):
        admin = db.session.get(Admin, admin_id)
        if admin:
            admin.device_id = device_id
            db.session.commit()
            return admin
        return None
    
    def check_user_device(self, user_id, device_id):
        user = db.session.get(User, user_id)
        if user:
            if user.device_id == device_id:
                return True
        return False
    
    def check_admin_device(self, admin_id, device_id):
        admin = db.session.get(Admin, admin_id)
        if admin:
            if admin.device_id == device_id:
                return True
        return False

    def get_user_by_email(self, user_email):
        user = User.query.filter_by(user_email=user_email).first() # db.session.get(User, email)
        if user:
            return user
        else:
            return None
        
    def search_users_by_name_or_email_or_id(self, search_term):
        users = User.query.filter(User.user_name.ilike('%'+search_term+'%')).all() # Use ilike() for case-insensitive search.
        return users
    
    def get_all_users(self):
        return User.query.all()
    
    def get_user_db_stat(self):
        return (User.query.count(), User.query.filter_by(user_status=1).count(), User.query.filter_by(user_status=0).count())
        
    def add_new_user(self, user_email, user_name, user_status=0):
        new_user = User(user_email=user_email, user_name=user_name, user_status=user_status)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def add_new_admin(self, admin_name, admin_email, hashed_password):
        new_admin = Admin(admin_name=admin_name, admin_email=admin_email, admin_password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()
        # db.session.delete(otp_attempts)  # Remove OTP record after success
        return new_admin
    
    def get_admin_by_email(self, admin_email):
        admin = Admin.query.filter_by(admin_email=admin_email).first()
        if admin:
            return admin
        return None
    
    def get_admin_by_username(self, admin_name):
        admin = Admin.query.filter_by(admin_name=admin_name).first()
        if admin:
            return admin
        return None
        
    def cheking_existing_admin(self, admin_email, admin_name):
        user = Admin.query.filter((Admin.admin_name == admin_name) | (Admin.admin_email == admin_email)).first()
        return user

    def update_admin_credentials(self, admin_email, hashed_password):
        admin = self.get_admin_by_email(admin_email = admin_email)
        admin.admin_password = hashed_password
        db.session.commit()
        return admin
    
    def admin_approve_user(self, user_id, admin_id, admin_email, admin_name):
        user = db.session.get(User, user_id)
        if user:
            user.user_status = 1
            db.session.commit()
            return user
        return None
    
    def admin_disapprove_user(self, user_id, admin_id, admin_email, admin_name):
        user = db.session.get(User, user_id)
        if user:
            user.user_status = 0
            db.session.commit()
            return user
        return None

    def notify_admins_of_new_user(self, user_email, user_name):
        for admin in Admin.query.with_entities(Admin.admin_email).all():
            new_user_added(admin.admin_email, user_email, user_name)

    def save_otp_attempt(self, admin_name, admin_email, admin_password, otp, tries):
        otp_attempt = newAdmin.query.filter_by(admin_email=admin_email).first()
        if otp_attempt:
            otp_attempt.otp = otp
            otp_attempt.tries = tries
            otp_attempt.last_attempt = datetime.now(timezone.utc)
        else:
            new_attempt = newAdmin(admin_name=admin_name, admin_email=admin_email, admin_password=admin_password, otp=otp, tries=tries, last_attempt=datetime.now(timezone.utc))
            db.session.add(new_attempt)
        db.session.commit()

    def load_otp_attempt(self,admin_email):
        return newAdmin.query.filter_by(admin_email=admin_email).first()
    
    def register_new_order(self, order_id, amount, currency, payment_status, user_id, booking_type):
        if not Payment.query.filter_by(order_id=order_id).first(): # order id must not exist and user must exist.
            if User.query.filter_by(user_id=user_id).first():
                new_order = Payment(order_id=order_id,
                                    amount=amount,
                                    currency=currency,
                                    payment_status= PaymentStatus.PENDING if payment_status == 'created' else PaymentStatus.ERROR,
                                    user_id=user_id,
                                    booking_type=booking_type,
                                    created_at=datetime.now(timezone.utc))
                db.session.add(new_order)
                db.session.commit()
                return True
            else:
                return False
        else:
            return False
        
    def payment_status_failed(self, order_id, payment_id, signature, user_id, method = PaymentMethod.UPI):
        payment = Payment.query.filter_by(order_id=order_id).first()
        if payment:
            if payment.user_id == user_id:
                payment.payment_status=PaymentStatus.FAILED
                payment.signature=signature
                payment.payment_id=payment_id
                payment.payment_method=method
                payment.failure_at=datetime.now(timezone.utc)
                db.session.commit()
                return True
            else:
                return False
        else:
            return False
        
    def payment_status_completed(self, order_id, payment_id, signature, user_id, method = PaymentMethod.UPI):
        payment = Payment.query.filter_by(order_id=order_id).first()
        user = User.query.filter_by(user_id=user_id).first()
        if payment:
            if payment.user_id == user_id:
                payment.payment_status=PaymentStatus.COMPLETED
                payment.signature=signature
                payment.payment_id=payment_id
                payment.payment_method=method
                payment.paid_at=datetime.now(timezone.utc)
                user.user_credits = user.user_credits + (payment.amount / 100)
                db.session.commit()
                return True
            else:
                return False
        else:
            return False

    def update_user_credits(self, user_id, amount = 0.01, service_name = 'SATYA'):
        user = User.query.filter_by(user_id=user_id).first()
        if user:
            user.user_credits -= Decimal(str(amount))
            db.session.commit()
            return True
        return False

if __name__ == "__main__":

    db_obj = Database()
    db_obj.save_otp_attempt("Vivek", "example@email.com", "abcdefgh1345678", "123456", 1)
    attempt = db_obj.load_otp_attempt("example@email.com")
    print(attempt.otp, attempt.tries, attempt.last_attempt)