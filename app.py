import os

# Library imports
from cs50 import SQL
from retrying import retry
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# Custom code imports
from helpers import *
from eosscript import *
from scrape import *

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Building the URI
uri = os.getenv("DATABASE_URL")
print(uri)
# Added for fl0 PaaS
uri += "&connect_timeout=10"
# Common to all PaaS
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")

# Connect with retry (added for Fl0 PasS)
@retry(
    stop_max_attempt_number=5,  # Number of retries before giving up
    wait_fixed=4000,            # Minimum time between retries in milliseconds
    retry_on_exception=lambda e: isinstance(e, RuntimeError),
    wrap_exception=True
)
def connect_with_retry():
    try:
        db = SQL(uri)
        return db
    except RuntimeError as e:
        raise e
    
# Calling connect with retry and getting the db set
db = connect_with_retry()


# Distribution code from finance
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Mostly own code from finance
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register to the app"""

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    # Retrive leagues form database to populate the field in the form
    leagues = db.execute("SELECT league FROM leagues")

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username. ")
            return redirect("/register")


        # Ensure name was submitted
        if not request.form.get("name"):
            flash("Must provide a name. ")
            return redirect("/register")

        # Ensure league was submited
        if not request.form.get("league"):
            flash("Please select your league from the menu. ")
            return redirect("/register")

        # Ensure league has a valid value
        if not any(d["league"] == request.form.get("league") for d in leagues):
            flash("Invalid group. ")
            return redirect("/register")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password. ")
            return redirect("/register")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("Must provide password confirmation. ")
            return redirect("/register")

        # Ensure password matches confirmation
        elif request.form.get("confirmation") != request.form.get("password"):
            flash("Password confirmation does not match password. ")
            return redirect("/register")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check if username already exists
        if len(rows) != 0:
            flash("Username already in use. ")
            return redirect("/register")


        # Hash password
        hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=16)
        # Variables for fields
        username = request.form.get("username")
        name = request.form.get("name")
        league = request.form.get("league")
        team = request.form.get("team")
        # Store new username and hashed password into the database
        id = db.execute("INSERT INTO users (username, fullname, league, team, hash) VALUES(?, ?, ?, ?, ?)", username, name, league, team, hash)
        # Remember which user has logged in
        session["user_id"] = id

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", status=status, leagues=leagues)


# Ditribution code from finance
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/login")

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username or password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", status=status)

# Distribution code from finance
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/settings")
@login_required
def settings():
    """ Update user registration data menu """

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    return render_template("settings.html", status=status)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """ Updates user password """

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("oldpassword"):
            flash("Must provide old password. ")
            return redirect("/password")

        rows = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Ensure old password is valid
        if not check_password_hash(rows[0]["hash"], request.form.get("oldpassword")):
            flash("Invalid old password. ")
            return redirect("/password")

        # Ensure new password is provided
        if not request.form.get("password"):
            flash("Must provide a new password. ")
            return redirect("/password")

        # Ensure new password is not same as old password
        if request.form.get("password") == request.form.get("oldpassword"):
            flash("New password can't be the same as old password. ")
            return redirect("/password")

        # Ensure confirmation is provided
        if not request.form.get("confirmation"):
            flash("Must provide a password confirmation. ")
            return redirect("/password")

        # Ensure password matches confirmation
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Confirmation must match the provided new password. ")
            return redirect("/password")

        # Generate new password hash
        hash = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=16)
        # Update Has in dtaabase
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash, session["user_id"])
        flash("New password has been set. ")
        return redirect("/password")

    else:
        return render_template("password.html", status=status)


@app.route("/data", methods=["GET", "POST"])
@login_required
def data():
    """ Updates user data """

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    # Retrieve current user's choices
    currentdata = db.execute("SELECT league, team FROM users WHERE id = ?", session["user_id"])
    currentdata = {"league": currentdata[0]["league"], "team": currentdata[0]["team"]}

    # Retrieve leagues form database to populate the field in the form
    leagues = db.execute("SELECT league FROM leagues")

    if request.method == "POST":

        # Get data from the form
        league = request.form.get("league")
        team = request.form.get("team")

        # Make suure submission is not empty
        if not league and not team:
            flash("Your submission cannot be empty. ")
            return redirect("/data")

        # List existent leagues
        leaguecheck = []
        for l in leagues:
            leaguecheck.append(l["league"])

        # If league input was provided
        if league:
            # Check it exists
            if league not in leaguecheck:
                flash("You must provide a valid group, or pick retired. ")
                return redirect("/data")
            # If exists, log in database
            db.execute("UPDATE users SET league = ? WHERE id = ?", league, session["user_id"])

        # If team input was provided
        if team:
            db.execute("UPDATE users SET team = ? WHERE id = ?", team, session["user_id"])


        flash("Your data has been successfully updated. ")
        return redirect("/data")

    else:
        return render_template("data.html", status=status, currentdata=currentdata, leagues=leagues)


@app.route("/")
def index():
    """Show current status of the game"""

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    if "user_id" in session:
        # if user is logged, Retrieve predictions
        currentpred = db.execute("SELECT predict.selection_id, selection.fullname, predict.tyres_id, tyres.brand FROM predict JOIN selection ON predict.selection_id = selection.selection_id JOIN tyres ON predict.tyres_id = tyres.tyres_id WHERE predict.user_id = ? AND predict.season_id = ? AND predict.league = 'Elite' ORDER BY selection.fullname", session["user_id"], current)
    else:
        currentpred = None

    # Retrieve what seasons needs displaying
    if status == "Closed":
        season = current
    elif status == "Open":
        season = int(current) - 1

        # Check if predictions
        if "user_id" in session:
            if currentpred == []:
                flash("You have no predictions placed yet")

    # Retrieve season data to display
    endofseason = db.execute("SELECT * FROM scores WHERE season = ? AND league = 'Elite'", season)
    assetaccuracy = db.execute("SELECT selection.fullname, tyres.brand, selection.pred_right, selection.pred_wrong, selection.total_pred FROM selection LEFT JOIN tyres ON selection.tyres_id = tyres.tyres_id WHERE selection.season = ? AND selection.league = 'Elite' AND selection.total_pred > 0", season)

    # Sort data by total score and tiebreaker criteria
    endofseason = sorted(endofseason, key=lambda k: (-k["total_score"], k["incorrect"], k["correct_p"]))
    # Sort by total number of predictions and right predictions
    assetaccuracy = sorted(assetaccuracy, key=lambda k: (-k["total_pred"], -k["pred_right"]))

    # Render template with needed data
    return render_template("index.html", endofseason=endofseason, assetaccuracy=assetaccuracy, status=status, currentpred=currentpred)


@app.route('/season/<number>')
@login_required
def old_seasons(number):
    """ Shows seasons standings for the required season """

    # Select data for the required season
    endofseason = db.execute("SELECT * FROM scores WHERE season = ? AND league = 'Elite'", number)
    assetaccuracy = db.execute("SELECT selection.fullname, tyres.brand, selection.pred_right, selection.pred_wrong, selection.total_pred FROM selection LEFT JOIN tyres ON selection.tyres_id = tyres.tyres_id WHERE selection.season = ? AND selection.league = 'Elite' AND selection.total_pred > 0", number)
    # Retrieve predictions
    currentpred = db.execute("SELECT predict.selection_id, selection.fullname, predict.tyres_id, tyres.brand FROM predict JOIN selection ON predict.selection_id = selection.selection_id JOIN tyres ON predict.tyres_id = tyres.tyres_id WHERE predict.user_id = ? AND predict.season_id = ? AND predict.league = 'Elite' ORDER BY selection.fullname", session["user_id"], number)
    if endofseason:
        # Sort data by total score and tiebreaker criteria
        endofseason = sorted(endofseason, key=lambda k: (-k["total_score"], k["incorrect"], k["correct_p"]))
        assetaccuracy = sorted(assetaccuracy, key=lambda k: (-k["total_pred"], -k["pred_right"]))
        # Render template with needed data
        return render_template("old_seasons.html", endofseason=endofseason,  assetaccuracy=assetaccuracy, currentpred=currentpred, season=number)
    else:
        flash("The selected season couldn't be found. ")
        return redirect("/")


@app.route('/seasons_search', methods=["GET", "POST"])
@login_required
def seasons_search():
    """ Processes the form to select old standings """

    seasons = db.execute("SELECT season FROM scores WHERE league = 'Elite'")
    seasons = [score['season'] for score in seasons]
    seasons = list(set(seasons))

    if request.method == "POST":
        searched_season = request.form.get("season")
        if int(searched_season) in seasons:
            return redirect(f"/season/{searched_season}")
        else:
            flash("The selected season couldn't be found. ")
            return redirect("/seasons_search")
    else:
        return render_template("seasons_form.html", seasons=seasons)


@app.route("/predict", methods=["GET", "POST"])
@login_required
def predict():
    """ Lets user predict tyres for the chosen assets """

    # Check for the current season
    current = db.execute("SELECT season FROM status WHERE current = 'True'")[0]["season"]
    # Check game status
    status = db.execute("SELECT status FROM status WHERE season = ?", current)[0]["status"]

    # Retrieve tyres from db
    tyres =  db.execute("SELECT tyres_id, brand FROM tyres WHERE season = ? AND league = 'Elite'", current)
    # List all tyres ids for later checks
    validtyres = [tyre["tyres_id"] for tyre in tyres]

    # Query for available assets to choose from
    managers = db.execute("SELECT selection_id, fullname FROM selection WHERE season = ? AND league = 'Elite' ORDER BY fullname", current)
    # List all selection ids for later checks
    validman = [manager["selection_id"] for manager in managers]

    # Query for already stored predictions
    predictions = db.execute("SELECT selection_id, tyres_id FROM predict WHERE user_id = ? AND season_id = ? AND league = 'Elite'", session["user_id"], current)
    lenpred = len(predictions)

    # Add new keys if there are existent predictions
    for manager in managers:
        for prediction in predictions:
            if manager["selection_id"] == prediction["selection_id"]:
                manager["selected"] = True
                manager["tyres_id"] = prediction["tyres_id"]

    # POST request
    if request.method == "POST":
        # Make sure no predicitions can be posted if season is closed 
        if status == "Closed":
            flash("Submissions for the season are closed. ")
            return redirect("/")
        
        # Colect data from form
        last_predictions = request.form.getlist("tyres")
        # Split manager id from tyre id
        last_predictions = [tuple(prediction.split("/")) for prediction in last_predictions if prediction != "not picked"]

        # Check if the form returned predictions
        if last_predictions == []:
            flash("Your prediction cannot be empty. ")
            return redirect("/predict")

        # Check for number of predictions cap
        if len(last_predictions) > 30:
            flash("You cannot pick more than 30 managers to predict tyres. ")
            return redirect("/predict")

        # Check manager ids and tyres ids are valid
        valid_prediction = [prediction for prediction in last_predictions if int(prediction[0]) in validman and int(prediction[1]) in validtyres]
        if last_predictions != valid_prediction:
            flash("Your prediction is invalid, please try again. ")
            return redirect("/predict")

        # If there are old predictions, remove them
        for prediction in predictions:
            db.execute("DELETE FROM predict WHERE selection_id = ? AND user_id = ? AND season_id = ?", prediction["selection_id"], session["user_id"], current)
        # Insert new predictions
        for prediction in last_predictions:
            db.execute("INSERT INTO predict (user_id, selection_id, tyres_id, season_id, league) VALUES (?, ?, ?, ?, 'Elite')", session["user_id"], prediction[0], prediction[1], current)

        flash("Your predictions have been saved!")
        return redirect("/")

    else:
        if status == "Closed":
            flash("Submissions for the season are closed. ")
            return redirect("/")

        if lenpred != 0:
            # Warn about edition overwrite
            flash("You have already submitted your predictions. Editing will overwrite them. ")
        # Render template
        return render_template("predict.html", lenpred=lenpred, predictions=predictions, status=status, managers=managers, tyres=tyres)


@app.route("/adminpanel")
@admin_access
def admin_panel():
    """ Admin friendly panel for updating the game """

    return render_template("adminpanel.html")


@app.route("/recoverpass", methods=["GET", "POST"])
@admin_access
def recover_password():
    """ Assist in password recovery """

    if request.method == "POST":

        # Hash password
        hash = generate_password_hash(request.form.get("newpass"), method='pbkdf2:sha256', salt_length=16)
        # Get username
        username = request.form.get("username")

        db.execute("UPDATE users SET hash = ? WHERE username = ?", hash, username)
        flash("Password update successful. ")
        return redirect("/recoverpass")

    else:
        return render_template("recoverpass.html")


@app.route("/tyresupdate")
@admin_access
def tyres_update():
    """ Scrape current season's available tyres for the league/s that will be part of the game """

    return scrape_brands(db)


@app.route("/assetsupdate")
@admin_access
def assets_update():
    """ Scrape the assets (players) for current season in the leagues that will be predicted """

    return scrape_names(db)


@app.route("/tyresselect")
@admin_access
def tyres_select():
    """ Scrapes asset's actual tyre choice for the season and updates it in the db """

    return scrape_managers_tyres(db)


@app.route("/gamestatus", methods=["GET", "POST"])
@admin_access
def newseason():
    """ Inserts the new season to the database and sets it as current - Updates status of past season"""

    if request.method == "POST":

        newseason = int(request.form.get("newseason"))

        # Set the last current season as false
        db.execute("UPDATE status SET current = 'False' WHERE current = 'True'")
        db.execute("INSERT INTO status (season, league, status, current) VALUES (?, 'Elite', 'Closed', 'True')", newseason)

        flash("New season has been input to the database and set as current. ")
        return redirect("/gamestatus")

    else:
        flash("Remember to close the old season before setting the new one. ")
        return render_template("gamestatus.html")


@app.route("/open")
@admin_access
def openseason():
    """ Opens current season """

    db.execute("UPDATE status SET status = 'Open' WHERE current = 'True'")

    flash("Current season has been set to Open. ")
    return redirect("/gamestatus")


@app.route("/closed")
@admin_access
def closeseason():
    """ Closes current season """

    db.execute("UPDATE status SET status = 'Closed' WHERE current = 'True'")

    flash("Current season has been set to Closed. ")
    return redirect("/gamestatus")


@app.route("/endofseason")
@admin_access
def endofseason():
    """ The big red button - Script that calculates scores for the game """

    return end_of_season(db)

