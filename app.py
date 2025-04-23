import os
import logging

from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Setup database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_change_in_production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fb_react_tool.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db.init_app(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Import routes and models after db is initialized to avoid circular imports
with app.app_context():
    from models import User, Token
    from forms import LoginForm, RegistrationForm, PostReactionForm, CommentReactionForm, TokenForm
    from utils import react_to_post, react_to_comment, convert_post_link, extract_comment_id_from_url
    
    # Create tables
    db.create_all()
    
    # Create admin user if it doesn't exist
    admin_email = "david143"
    admin_password = "david1433"
    
    # Try to find admin by email
    admin_user = User.query.filter_by(email=admin_email).first()
    
    # If admin doesn't exist, create one
    if not admin_user:
        from werkzeug.security import generate_password_hash
        logging.debug(f"Creating admin user: {admin_email}")
        admin_user = User(
            username="admin",
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()  # Commit first to get the admin ID
        
        # Add default tokens
        default_tokens = [
            "EAAAAUaZA8jlABOZBpufawJh9bMbHBn645cUjZCHNk36osnOMlQgYx8l7yRqsdTibDIU3rdTZBmW22AV21iPl1UnZBOAN5WhrZCEQtZCNnS9p7zxKMlRKuEPW9Nux2LSkyas35WTxZCJdZCjZApjD5QPXZA81XndOIL1Mv9MCtWVtfAK3ZBoNajrFqP55de5Ew9HNWLwG8psi6rkLVQZDZD",
            "EAAAAUaZA8jlABO66bNohz7DaZCxZBkqZCtJLW3s3IDMrhepAGFP0nFm75UTN2mumDVXJ1EdyxJ4CaIPZCnfKzDrHnSw1CEUrtGEF32vptg28BkY0dQ11ojkTGAAwXA4FvYAIh111BbbNVdNULglH7x8W4rrqTNVHwdB3jZAcoZBX0Nr7DY5ZBXAVKF8Qf15SAYAN7nLcnZCTn3ugZDZD",
            "EAAAAUaZA8jlABO5zZBlCvDHUYzQv1x4leVJ6ZCVYx3JJmfqQwMiTGZBJV6KTSZChUTeZA87PWuEUhh9OuFjQIT7gOyHwIJyDXVK7DtHd3YtFqZAFpmFT6D2D7MXLPz10eOO453QuOScbDQBEqy3eKeFP3IRgZAr3EQmlUKG8GGsZB6T8JgPaiXhgeezZCQaYNdOWveqs1cRAZDZD",
            "EAAAAUaZA8jlABO7uPnNo9ijv0aKllfyC38uO3v9ONsJZBaZBRIrNYe1uZAIZCKB3pmBcwfRseFnxhHVfAzDdiZARctLI0DPvzvuWKvqWYyZBRbhuT0hVklODgoj3uYCJhHP5w0PfbcHPo1u6FRAR2QgZBrqmR7EqPILf7WI3tJHnIz8hhO9bddsfQOndyvHleVUszX0TaQZDZD"
        ]
        
        for token_value in default_tokens:
            token = Token(value=token_value, added_by=admin_user.id)
            db.session.add(token)
        
        db.session.commit()
        logging.info("Admin user and default tokens created")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Log debugging info
        logging.debug(f"Login attempt for email: {email}")
        
        # Handle admin login case directly
        if email == "david143" and password == "david1433":
            admin = User.query.filter_by(email=email).first()
            if admin:
                login_user(admin, remember=form.remember.data)
                flash('Admin login successful!', 'success')
                return redirect(url_for('dashboard'))
        
        # Normal user login flow
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        from werkzeug.security import generate_password_hash
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/post-reaction', methods=['GET', 'POST'])
@login_required
def post_reaction():
    form = PostReactionForm()
    
    if form.validate_on_submit():
        post_url = form.post_url.data
        reaction_type = form.reaction_type.data
        count = form.count.data
        
        post_id = convert_post_link(post_url)
        if not post_id:
            flash('Invalid post URL.', 'danger')
            return render_template('post_reaction.html', form=form)
        
        tokens = Token.query.all()
        if not tokens:
            flash('No tokens available. Please contact the admin.', 'danger')
            return render_template('post_reaction.html', form=form)
        
        # Process reactions
        success = 0
        failed = 0
        
        import random
        for _ in range(count):
            token = random.choice(tokens).value
            result = react_to_post(token, post_id, reaction_type)
            if result and 'success' in result:
                success += 1
            else:
                failed += 1
        
        flash(f'Reaction completed! Success: {success}, Failed: {failed}', 'success')
        return redirect(url_for('post_reaction'))
    
    return render_template('post_reaction.html', form=form)

@app.route('/comment-reaction', methods=['GET', 'POST'])
@login_required
def comment_reaction():
    form = CommentReactionForm()
    
    if form.validate_on_submit():
        comment_url = form.comment_url.data
        reaction_type = form.reaction_type.data
        count = form.count.data
        
        comment_id = extract_comment_id_from_url(comment_url)
        if not comment_id:
            flash('Invalid comment URL.', 'danger')
            return render_template('comment_reaction.html', form=form)
        
        tokens = Token.query.all()
        if not tokens:
            flash('No tokens available. Please contact the admin.', 'danger')
            return render_template('comment_reaction.html', form=form)
        
        # Process reactions
        success = 0
        failed = 0
        
        import random
        for _ in range(count):
            token = random.choice(tokens).value
            result = react_to_comment(token, comment_id, reaction_type)
            if result and 'success' in result:
                success += 1
            else:
                failed += 1
        
        flash(f'Reaction completed! Success: {success}, Failed: {failed}', 'success')
        return redirect(url_for('comment_reaction'))
    
    return render_template('comment_reaction.html', form=form)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    
    user_count = User.query.count()
    token_count = Token.query.count()
    
    return render_template('admin/dashboard.html', user_count=user_count, token_count=token_count)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    
    if current_user.id == user_id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/tokens', methods=['GET', 'POST'])
@login_required
def admin_tokens():
    if not current_user.is_admin:
        abort(403)
    
    form = TokenForm()
    
    if form.validate_on_submit():
        token = Token(
            value=form.token.data,
            added_by=current_user.id
        )
        db.session.add(token)
        db.session.commit()
        
        flash('Token added successfully.', 'success')
        return redirect(url_for('admin_tokens'))
    
    tokens = Token.query.all()
    return render_template('admin/tokens.html', tokens=tokens, form=form)

@app.route('/admin/token/delete/<int:token_id>', methods=['POST'])
@login_required
def delete_token(token_id):
    if not current_user.is_admin:
        abort(403)
    
    token = Token.query.get_or_404(token_id)
    db.session.delete(token)
    db.session.commit()
    
    flash('Token has been deleted.', 'success')
    return redirect(url_for('admin_tokens'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)