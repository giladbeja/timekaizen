import os
import requests
import urllib.parse
import datetime
from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def datecalc(d, m, y):
    d1 = datetime.datetime.now()
    d2 = datetime.datetime(day=d, month=m, year=y)
    countdown=d2-d1
    dr = countdown.days
    dremaining = dr+2
    return dremaining
    
    