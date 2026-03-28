from splid_app.db import  get_db
from splid_app.auth import login_required
from splid_app.users import get_users
from flask import( 
    Blueprint, g, flash, redirect, render_template, request, url_for
)

bp = Blueprint('trips',__name__,url_prefix=('/trips'))

@bp.route('/add',methods=('POST','GET'))
@login_required
def new_trip():
    if request.method == 'POST':
        trip_name = request.form['trip_name']
        user_ids = request.form.getlist('user_ids')
        error = None

        if not trip_name:
            error = 'Trip name is required'
        elif not user_ids:
            error = 'Select users for this trip'
        
        if error is not None:
            flash(error)
        else:
            user_ids.append(g.user['id']) #Adding the person creating the trip into the users list
            db = get_db()
            cursor = db.execute(''' INSERT INTO trips (trip_name, creator_id) VALUES (?,?)''',
                                (trip_name,g.user['id'])
                                )
            trip_id = cursor.lastrowid
            add_users_into_trip(user_ids, trip_id)
            db.commit() #probs better to only commit here. But ive commited inside the sub function too
    users = get_users()
    return render_template('trips/add.html', users = users)


def add_users_into_trip(users,trip_id):
    db = get_db()
    for user in users:
        db.execute(''' INSERT INTO usersInTrip (user_id, trip_id) VALUES (?,?)''',(user, trip_id)
        )
    #LEARNING - moved the commit outside loop so it's more efficient
    db.commit()

def list_trips(user_id):
    db = get_db()
    trip_list = db.execute('''SELECT id, trip_name, created
               FROM trips
               WHERE creator_id = ?''', (user_id,)
               ).fetchall()
    return trip_list
    
def get_users_in_trip(trip_id):
    db = get_db()
    users_in_trip = db.execute(''' 
               SELECT users.name, users.id
               FROM usersInTrip
               JOIN users on users.id = usersInTrip.user_id
               WHERE usersInTrip.trip_id = ? ''', (trip_id,)).fetchall()
    return users_in_trip

#Need to make it impossible to view other peoples trips
@bp.route('/<int:id>',methods=('GET', 'POST'))
@login_required
def trip_page(id):
    trip_id = id
    users = get_users_in_trip(trip_id)

    return render_template('trips/trip.html', users=users)