from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship to tokens
    tokens = db.relationship('Token', backref='creator', lazy=True, 
                            primaryjoin="User.id==Token.added_by")
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(512), unique=True, nullable=False)
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"Token('{self.id}', Added by: {self.added_by})"
