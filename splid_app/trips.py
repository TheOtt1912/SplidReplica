#Fun Improvements: 1) Creator a decorator for trip_member_required , rather than having this func thats constantly called

from splid_app.db import  get_db
from splid_app.auth import login_required
from splid_app.users import get_users
from flask import( 
    Blueprint, g, flash, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

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
    trip_list = db.execute('''SELECT trips.id, trips.trip_name, trips.created
               FROM usersInTrip
               JOIN trips on trips.id = usersInTrip.trip_id
               WHERE usersInTrip.user_id = ?''', (user_id,)).fetchall()
    return trip_list

def get_users_in_trip(trip_id):
    db = get_db()
    users_in_trip = db.execute(''' 
               SELECT users.name, users.id
               FROM usersInTrip
               JOIN users on users.id = usersInTrip.user_id
               WHERE usersInTrip.trip_id = ? ''', (trip_id,)).fetchall()
    return users_in_trip


def get_trip(id, check_user=True):
    db = get_db()
    trip = db.execute(''' SELECT * FROM trips
                   WHERE id = ?''',(id,)).fetchone()
    is_in_trip = is_user_in_trip(id)
    
    if trip is None:
        abort(404, f'Trip with id {id}, doesnt exist.')
        
    if check_user == True and is_in_trip == False:
        abort(403)
    
    else:
        return trip


def is_user_in_trip(id):
    users_in_trip = get_users_in_trip(id)
    
    for user in users_in_trip:
        if g.user['id'] == user['id']:
            return True
    return False

######################## TripPage ###########################


@bp.route('/<int:id>',methods=('GET', 'POST'))
@login_required
def trip_page(id):
    get_trip(id)
    users = get_users_in_trip(id)
    user_ids = [user['id'] for user in users]

    ledger = owed_to_user_in_trip(id, user_ids)

    return render_template('trips/trip.html', users=users, id = id, ledger = ledger)

######################## TRANSACTIONS ###########################

@bp.route('/<int:id>/tx_add',methods=('POST','GET'))
@login_required
def new_transaction(id):
    get_trip(id)
    if request.method == 'POST':
        amount = request.form['amount']
        title = request.form['title']
        user_ids = request.form.getlist('user_ids')
        error = None

        if not amount:
            error = 'Please enter an amount.'
        elif not title:
            error = 'Please enter a title'
        elif not user_ids:
            error = 'Please select atleast one person to split with.'
        if error is not None:
            flash(error)
        
        else:
            db = get_db()
            cursor = db.execute(''' INSERT INTO transactions (title, amount, trip_id, user_id) VALUES (?,?,?,?)''',
                                (title,amount, id, g.user['id'])
                                )
            transaction_id = cursor.lastrowid
            add_debts(transaction_id,amount,user_ids)
            db.commit()
        
        return redirect(url_for('trips.trip_page', id=id))
    users = get_users_in_trip(id)
    return render_template('trips/tx_add.html',users=users)

def add_debts(transaction_id,amount,users):
    num_of_users = len(users) + 1 #for the creator who the bill is also split by
    debt_amount = (int(amount) / num_of_users)
    db = get_db()
    for user in users:
        db.execute(''' INSERT INTO debts (transaction_id, owed_by_id, amount,status) VALUES (?,?,?,?)''',(transaction_id,user,debt_amount,'owing')
        )

#Gonna make a dict baby
#The result should be dictionary with each user_id who owes me, and their amount owed to me
#eg. {1:90.0, 2:300.0}
def owed_to_user_in_trip(trip_id,user_ids):
    db = get_db()
    owed_to_ledger = {}

    for user in user_ids:
       x = db.execute(''' SELECT SUM(debts.amount)
                   FROM debts
                   JOIN transactions on transactions.id = debts.transaction_id
                   WHERE transactions.trip_id = ? AND transactions.user_id = ? AND debts.owed_by_id = ? ''', (trip_id,g.user['id'], user)
        ).fetchone()
       owed_to_ledger[user] = x[0]
    
    return owed_to_ledger

#def user_owes_in_trip(trip_id,users)