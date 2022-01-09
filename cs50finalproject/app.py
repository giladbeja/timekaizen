from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask.helpers import get_flashed_messages
from flask_session import Session
from helpers import login_required, datecalc
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from bs4 import BeautifulSoup
import os

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.1.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        items = db.execute(
            "SELECT Todo, DueDate, Daysremaining FROM Todo WHERE userID = ? ORDER BY Daysremaining;",
            session["user_id"],
        )
        return render_template(
            "index.html", items=items
       )
    else:
        db.execute("DELETE FROM Todo WHERE Daysremaining IS NOT NULL LIMIT 1")
        items = db.execute(
            "SELECT Todo, DueDate, Daysremaining FROM Todo WHERE userID = ? ORDER BY Daysremaining;",
            session["user_id"],
        )
        return render_template("index.html", items=items)

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add item to todo list"""
    if request.method == "POST":
        item = request.form.get("add")
        date = request.form.get("date")
        
        a,b,c = date.split('-')
        y = int(a)
        m = int(b)
        d = int(c)
        print(datecalc(d, m, y))
        if not item:
            return apology("Please enter an assignment to do", 400)
        elif not date:
            return apology("Please enter a due date", 400)
        remaindays = datecalc(d, m, y)
        db.execute(
                "INSERT INTO Todo (userID, Todo, DueDate, Daysremaining) VALUES (?, ?, ?, ?)",
                session["user_id"],
                item,
                date,
                remaindays
            )
        flash("Successfully Added Item to List")
        return redirect("/")
    else:
        return render_template("add.html")
        
    


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide username")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please provide password")
            return render_template("login.html")
        # Query database for username
        users = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(users) != 1 or not check_password_hash(
            users[0]["hash"], request.form.get("password")
        ):
            flash("Incorrect username or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = users[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure the username was submitted
        if not username:
            flash("Please provide username")
            return render_template("register.html")
        # Ensure the username doesn't exists
        elif len(rows) != 0:
            flash("Username already exists")
            return render_template("register.html")

        # Ensure password was submitted
        elif not password:
            flash("Please provide password")
            return render_template("register.html")

        # Ensure confirmation password was submitted
        elif not request.form.get("confirmation"):
            flash("Please confirm password")
            return render_template("register.html")

        # Ensure passwords match
        elif not password == confirmation:
            flash("Password does not match confirmation")
            return render_template("register.html")

        else:
            # Generate the hash of the password
            hash = generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=8
            )
            # Insert the new user
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?) ", username, hash,
            )
            # Redirect user to home page
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return redirect("/")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
