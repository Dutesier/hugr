import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

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

# ///////////////////////////////////////////////////////////////////////////

# HUGR database
db = SQL("sqlite:///project.db")

# Landing page
@app.route("/")
def index():
    return render_template("index.html")

# Log in
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        fname = rows[0]["fname"]

        # Redirect user to home page
        return render_template("home.html", fname=fname)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

        # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure username was submitted
        if not request.form.get("fname"):
            return apology("must provide first name", 403)

        # Ensure username was submitted
        if not request.form.get("lname"):
            return apology("must provide last name", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmedpassword was submitted
        elif not request.form.get("confirmpassword"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows) > 0:
            return apology("Username already exists", 403)

        username = request.form.get("username")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        # Check if password is same as confirmedpassword
        if request.form.get("password") != request.form.get("confirmpassword"):
            return apology("Password and Confirm Password must match", 403)

        # Hash password
        hashed = generate_password_hash(request.form.get("password"))

        # Insert user into database
        db.execute("INSERT INTO users (username, fname, lname, hash) VALUES (:username, :fname, :lname, :hashed)", username = username, fname= fname, lname= lname, hashed=hashed )
        userwheel = db.execute("SELECT id FROM users WHERE username = :username", username=username)
        user_id = userwheel[0]['id']
        db.execute("INSERT INTO wheel (user_id, leisure, environment, health, career, personal_dev, relationships, romance, finance) VALUES (:user_id, 50, 50, 50, 50, 50, 50, 50, 50)", user_id = user_id)
        return redirect("/login")

@app.route("/home")
@login_required
def home():
    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
    fname = rows[0]["fname"]

    return render_template("home.html", fname=fname)

@app.route("/wheel", methods=["GET", "POST"])
@login_required
def wheel():
    if request.method == "GET":
        user_id = session["user_id"]
        wheel = db.execute("SELECT leisure, environment, health, career, personal_dev, relationships, romance, finance FROM wheel WHERE user_id = :user_id", user_id=user_id)
        leisure = wheel[0]["leisure"]
        environment = wheel[0]["environment"]
        health = wheel[0]["health"]
        career = wheel[0]["career"]
        personal_dev = wheel[0]["personal_dev"]
        relationships = wheel[0]["relationships"]
        romance = wheel[0]["romance"]
        finance = wheel[0]["finance"]

        return render_template("wheel.html", leisure=leisure, environment=environment, health=health, career=career, personal_dev=personal_dev, relationships=relationships, romance=romance, finance=finance)

    else:
        # Ensure area was submitted
        if not request.form.get("area"):
            return apology("must provide an area", 403)

        # Ensure lvl of satisfaction was submitted
        elif not request.form.get("value"):
            return apology("must provide lvl of satisfaction", 403)

        user_id = session["user_id"]
        area = request.form.get("area")
        if area == "Personal Development":
            area = "personal_dev"
        value = request.form.get("value")

        db.execute("UPDATE wheel SET :area = :value WHERE user_id = :user_id", area=area, value=value, user_id=user_id)
        wheel = db.execute("SELECT leisure, environment, health, career, personal_dev, relationships, romance, finance FROM wheel WHERE user_id = :user_id", user_id=user_id)
        leisure = wheel[0]["leisure"]
        environment = wheel[0]["environment"]
        health = wheel[0]["health"]
        career = wheel[0]["career"]
        personal_dev = wheel[0]["personal_dev"]
        relationships = wheel[0]["relationships"]
        romance = wheel[0]["romance"]
        finance = wheel[0]["finance"]

        return render_template("wheel.html", leisure=leisure, environment=environment, health=health, career=career, personal_dev=personal_dev, relationships=relationships, romance=romance, finance=finance)

@app.route("/leisure")
@login_required
def leisure():
    user_id = session["user_id"]
    leisure = db.execute("SELECT leisure FROM wheel WHERE user_id= :user_id", user_id=user_id)
    level = leisure[0]["leisure"]

    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
    fname = rows[0]["fname"]

    db.execute("DELETE FROM strenght WHERE user_id = :user_id", user_id=user_id)
    db.execute("INSERT INTO strenght (user_id) VALUES (:user_id)", user_id=user_id)

    return render_template("leisure.html", level=level, fname=fname)

@app.route("/environment", methods=["GET", "POST"])
@login_required
def environment():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        x = request.form.getlist("area")
        a = 0
        for item in x:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET leisure = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        leisure = db.execute("SELECT leisure FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = leisure[0]["leisure"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("environment.html", level=level, fname=fname)

@app.route("/health", methods=["GET", "POST"])
@login_required
def health():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET environment = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        environment = db.execute("SELECT environment FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = environment[0]["environment"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("health.html", level=level, fname=fname)

@app.route("/career", methods=["GET", "POST"])
@login_required
def career():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET health = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        health = db.execute("SELECT health FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = health[0]["health"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("career.html", level=level, fname=fname)

@app.route("/personal_dev", methods=["GET", "POST"])
@login_required
def personal_dev():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET career = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        career = db.execute("SELECT career FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = career[0]["career"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("personal_dev.html", level=level, fname=fname)

@app.route("/relationships", methods=["GET", "POST"])
@login_required
def relationships():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET personal_dev = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        personal_dev = db.execute("SELECT personal_dev FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = personal_dev[0]["personal_dev"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("relationships.html", level=level, fname=fname)

@app.route("/romance", methods=["GET", "POST"])
@login_required
def romance():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET relationships = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        relationships = db.execute("SELECT relationships FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = relationships[0]["relationships"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("romance.html", level=level, fname=fname)

@app.route("/finance", methods=["GET", "POST"])
@login_required
def finance():
    if request.method == "GET":
        return redirect("/leisure")
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1

        user_id = session["user_id"]
        db.execute("UPDATE strenght SET romance = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        romance = db.execute("SELECT romance FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = romance[0]["romance"]

        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
        fname = rows[0]["fname"]

        return render_template("finance.html", fname=fname)

@app.route("/key_areas", methods=["GET", "POST"])
@login_required
def key_areas():
    user_id = session["user_id"]
    if request.method == "GET":

        areas = db.execute("SELECT leisure, environment, health, career, personal_dev, relationships, romance, finance FROM strenght WHERE user_id = :user_id", user_id=user_id)
        key_areas = areas[0]
        # Find item with Max Value in Dictionary
        itemMaxValue = max(key_areas.items(), key=lambda x: x[1])

        listOfKeys = list()
        # Iterate over all the items in dictionary to find keys with max value
        for key, value in key_areas.items():
            if value == itemMaxValue[1]:
                listOfKeys.append(key)

        return render_template("key_areas.html", listOfKeys=listOfKeys)
    else:

        d = request.form.getlist("area")
        a = 0
        for item in d:
            a +=1


        db.execute("UPDATE strenght SET finance = :a WHERE user_id = :user_id", a=a, user_id=user_id)

        finance = db.execute("SELECT finance FROM wheel WHERE user_id= :user_id", user_id=user_id)
        level = finance[0]["finance"]

        areas = db.execute("SELECT leisure, environment, health, career, personal_dev, relationships, romance, finance FROM strenght WHERE user_id = :user_id", user_id=user_id)
        key_areas = areas[0]
        # Find item with Max Value in Dictionary
        itemMaxValue = max(key_areas.items(), key=lambda x: x[1])

        listOfKeys = list()
        # Iterate over all the items in dictionary to find keys with max value
        for key, value in key_areas.items():
            if value == itemMaxValue[1]:
                listOfKeys.append(key)

        return render_template("key_areas.html", listOfKeys=listOfKeys)

@app.route("/new_plan")
@login_required
def new_plan():

    user_id = session["user_id"]
    rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=user_id)
    fname = rows[0]["fname"]

    return render_template("new_plan.html", fname=fname)

@app.route("/plan", methods=["GET", "POST"])
@login_required
def plan():

    # Variables
    user_id = session["user_id"]



    if request.method == "GET":

        # Access database for existing plans
        plans = db.execute("SELECT * FROM plans WHERE user_id = :user_id AND completion = 0", user_id=user_id)

        return render_template("plan.html", plans=plans)
    else:

        if not request.form.get("completion"):
            # Variables
            area = request.form.get("area")
            goal = request.form.get("goal")
            date = request.form.get("date")
            last_step = request.form.get("last_step")
            last_step1 = request.form.get("last_step1")
            last_step2 = request.form.get("last_step2")
            last_step3 = request.form.get("last_step3")
            last_step4 = request.form.get("last_step4")
            last_step5 = request.form.get("last_step5")
            last_step6 = request.form.get("last_step6")
            last_step7 = request.form.get("last_step7")
            last_step8 = request.form.get("last_step8")
            last_step9 = request.form.get("last_step9")
            last_step10 = request.form.get("last_step10")



            # Store in database
            db.execute("INSERT INTO plans (user_id, area, goal, date, last_step, last_step1, last_step2, last_step3, last_step4, last_step5, last_step6, last_step7, last_step8, last_step9, last_step10) VALUES (:user_id, :area, :goal, :date, :last_step, :last_step1, :last_step2, :last_step3, :last_step4, :last_step5, :last_step6, :last_step7, :last_step8, :last_step9, :last_step10)", user_id=user_id, area=area, goal=goal, date=date, last_step=last_step, last_step1=last_step1, last_step2=last_step2, last_step3=last_step3, last_step4=last_step4, last_step5=last_step5, last_step6=last_step6, last_step7=last_step7, last_step8=last_step8, last_step9=last_step9, last_step10=last_step10 )

        else:

            completion = request.form.get("completion")
            db.execute("UPDATE plans SET completion = 1 WHERE plan_id = :completion", completion=completion)
            # Access database for existing plans

        plans = db.execute("SELECT * FROM plans WHERE user_id = :user_id AND completion = 0", user_id=user_id)

        return render_template("plan.html", plans=plans)

@app.route("/history")
@login_required
def history():

    # Variables
    user_id = session["user_id"]
    plans = db.execute("SELECT * FROM plans WHERE user_id = :user_id", user_id=user_id)

    return render_template("history.html", plans=plans)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



# ///////////////////////////////////////////////////////////////////////////


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)