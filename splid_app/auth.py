import functools
import logging
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from splid_app.db import  get_db

bp = Blueprint('auth',__name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@bp.route('/register', methods=('GET','POST'))
def register(): #Register view function
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not name:
            error = 'Name is required.'
        elif not email:
            error = 'Email is required'
        elif not password:
            error = 'Password is required.'
        
        
        if error is None:
            try:
                db.execute(
                    """ INSERT INTO users (name, email, password) VALUES (?,?, ?) """, (name, email, generate_password_hash(password)),
                )
                db.commit()
                logger.info(f'New user registered: {email}')
            except db.IntegrityError:
                error = f"User {email} is already registered."
                logger.warning(f'Registration failed - email already exists: {email}')
            else:
                return redirect(url_for('auth.login'))
        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(''' SELECT * FROM users WHERE email = ? ''', (email,)
        ).fetchone()

        if user is None:
            error = 'Incorrect email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('home.home_page')) #url_for takes the blueprint name and function name, not the URL path.
        flash(error)
    return render_template('auth/login.html')

#bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested. 
# load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database, 
# storing it on g.user, which lasts for the length of the request. If there is no user id, or if the id doesn’t exist, g.user will be None.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(''' SELECT * FROM users WHERE id = ?''', (user_id,)                                  
                                  ).fetchone()


#TODO add the URL for. Its basically needed for this whole page
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

