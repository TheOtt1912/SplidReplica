from splid_app.db import  get_db
from flask import( 
    Blueprint, flash, redirect, render_template, request, url_for
)

bp = Blueprint('users',__name__,url_prefix='/users')


def get_users():
    db = get_db()
    user_list = db.execute(''' SELECT id, name, email FROM users
                           ''').fetchall()
    return user_list