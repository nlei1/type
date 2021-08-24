# Used some code from finance 50 staff solutions
import os
import re
import detectlanguage
import textstat
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, get_entities_dict, get_sentiment, spelling, get_related_words


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
db = SQL("sqlite:///typeapp.db")

@app.route("/")
@login_required
def index():
    """Show preview page"""
    paragraphs = db.execute("SELECT id, topic, content FROM paragraphs WHERE user=? ORDER BY id", session["user_id"])
    return render_template("index.html", paragraphs=paragraphs)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Show add paragraoh page"""
    # POST
    if request.method == "POST":
        if not request.form.get("topic"):
            return apology("missing topic")

        paragraph_topic = request.form.get("topic")

        rows = db.execute("SELECT topic FROM paragraphs WHERE user = ? AND topic = ?", session["user_id"], paragraph_topic)
        if rows:
            return apology("you've already created a paragraph of the same exact name")

        # Update sqlite tables to with info about the newest paragraph

        db.execute("INSERT INTO paragraphs (user, topic, content) VALUES(?, ?, ?)",
                   session["user_id"], paragraph_topic, "Temp placeholder.")

        rows = db.execute("SELECT id FROM paragraphs WHERE user = ? AND topic = ?", session["user_id"], paragraph_topic)
        paragraph_id = rows[0]['id']

        db.execute("INSERT INTO history (paragraph, topic, content) VALUES(?, ?, ?)",
                   paragraph_id, paragraph_topic, "Temp placeholder.")

        flash("Added a new paragraph, named " + paragraph_topic)

        return redirect("/")

    # GET
    else:
        return render_template("add.html")


@app.route("/share", methods=["GET", "POST"])
@login_required
def share():
    """Show post to social page"""
    # POST
    if request.method == "POST":
        if not request.form.get("topic"):
            return apology("write something first")

        # Updates sqlite tables with this new social post

        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        db.execute("INSERT INTO social (username, content) VALUES(?, ?)", username[0]['username'], request.form.get("topic"))
        flash("Added your project status update!")
        return redirect("social")

    # GET
    else:
        return render_template("share.html")


@app.route("/write", methods=["GET", "POST"])
@login_required
def write_paragraph():
    """Show write a paragraph page"""
    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("topic"):
            return apology("missing topic")
        if not request.form.get("content"):
            return apology("missing content")

        # Update sqlite table to insert contents of the new paragraph

        rows = db.execute("SELECT id FROM paragraphs WHERE user = ? AND topic = ?", session["user_id"], request.form.get("topic"))
        paragraph_id = rows[0]['id']

        db.execute("INSERT INTO history (paragraph, topic, content) VALUES(?, ?, ?)", paragraph_id, request.form.get("topic"), request.form.get("content"))

        db.execute("UPDATE paragraphs SET content = ? WHERE user = ? AND topic = ?", request.form.get("content"), session["user_id"], request.form.get("topic"))

        flash("Modified the content of the paragraph named " + request.form.get("topic"))

        return redirect("/")

    # GET
    else:
        # Get valid topics
        rows = db.execute("SELECT topic FROM paragraphs WHERE user = ?", session["user_id"])
        topics = [row["topic"] for row in rows]

        # Display sales form
        return render_template("write.html", topics=topics)


@app.route("/version")
@login_required
def version():
    """Show version control (history) page"""

    # Using sqlite commands to show editing history of the essay
    paragraphs = db.execute("SELECT * FROM history WHERE paragraph in (SELECT id FROM paragraphs WHERE user=?)", session["user_id"])
    return render_template("version.html", paragraphs=paragraphs)


# Code from finance50 staff solution
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide project name", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid project name and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        flash("Welcome, " + request.form.get("username") + "!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# Code from finance50 staff solution
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Should be similar to login()
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide valid project name", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password==repassword
        elif (request.form.get("password") != request.form.get("confirmation")):
            return apology("they aint the same", 400)

        u_name = request.form.get("username")
        p_word = request.form.get("password")

        hash = generate_password_hash(p_word)

        u_name_existing = db.execute("SELECT * FROM users WHERE username = ?", u_name)

        if len(u_name_existing) != 0:
            return apology("project name already taken", 400)

        else:
            registered = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", u_name, hash)

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/stats", methods=["GET", "POST"])
@login_required
def stats():
    """Show stats page"""
    paragraphs = db.execute("SELECT id, topic, content FROM paragraphs WHERE user=? ORDER BY id", session["user_id"])

    # return apology if user has no essay written yet
    if not paragraphs:
        return apology("Add a topic first")

    # create empty string where we will store all contents of the paragraph
    text_combined = ""

    # iterate through every paragraph
    for paragraph in paragraphs:

        # add its content into a string
        text_combined += paragraph["content"] + " "
    basics_facts = {}
    basics_facts['word_count'] = len(text_combined.split())
    basics_facts['char_count'] = len(text_combined)

    # dict of random facts
    facts = { 'syllables': textstat.syllable_count(text_combined), 'sentences': textstat.sentence_count(text_combined), 'flesch': textstat.flesch_reading_ease(text_combined), 'kincaid': textstat.flesch_kincaid_grade(text_combined), 'fog': textstat.gunning_fog(text_combined), 'smog': textstat.smog_index(text_combined), 'automated': textstat.automated_readability_index(text_combined), 'coleman': textstat.coleman_liau_index(text_combined), 'linsear': textstat.linsear_write_formula(text_combined), 'dale': textstat.dale_chall_readability_score(text_combined), 'consensus': textstat.text_standard(text_combined, float_output=False) }
    print(facts)

    entities_tools = get_entities_dict(text_combined)
    entities = entities_tools[0]
    print(entities)

    related_mentioned_keywords = entities_tools[1]

    research_wiz = {}
    for p_word in related_mentioned_keywords:
        research_wiz[p_word] = get_related_words(p_word)

    print('here are related words:')
    print(research_wiz)


    sentiment = get_sentiment(text_combined)
    print(sentiment)

    suggestions = spelling(text_combined)
    print(suggestions)

    return render_template("stats.html", basics_facts=basics_facts, suggestions=suggestions, sentiment=sentiment, entities=entities, paragraphs=paragraphs, facts=facts, text_combined=text_combined, research_wiz=research_wiz)


@app.route("/social")
@login_required
def social():
    """Show social page; display posts from all users"""

    # Using a sqlite call to select all of the posts from every single user
    posts = db.execute("SELECT username, content, timemstamp FROM social ORDER BY timemstamp DESC")
    return render_template("social.html", posts=posts)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
