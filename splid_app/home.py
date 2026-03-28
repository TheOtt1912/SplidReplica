from splid_app.db import  get_db
from splid_app.auth import login_required
from splid_app.users import get_users
from splid_app.trips import list_trips
from flask import( 
    Blueprint, g, flash, redirect, render_template, request, url_for
)

bp = Blueprint('home',__name__, url_prefix=('/home'))

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home_page():
    logged_in_user = g.user['id']
    trips = list_trips(logged_in_user)
    print(trips)

    return render_template('home/home.html',trips=trips)