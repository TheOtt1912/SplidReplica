import os
from flask import Flask, session, redirect, url_for


#The init is the file in which we 'create the app'. As the docs explained, this is the app factory.
def create_app(test_config=None):
    #create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #load the test config if passed in
        app.config.from_mapping(test_config)
 # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/hello')
    def hello():
        return 'This is splid replica'
    
    from . import db
    db.init_app(app)

    from . import trips
    app.register_blueprint(trips.bp)

    from . import users
    app.register_blueprint(users.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import home
    app.register_blueprint(home.bp)

    @app.route('/')
    def index():
        return redirect(url_for('home.home_page'))

    return app
