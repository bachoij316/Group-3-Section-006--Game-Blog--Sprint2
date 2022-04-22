# pylint: disable=invalid-envvar-default, unused-import, pointless-string-statement, no-member, invalid-name, no-else-return, too-few-public-methods, consider-using-f-string

"""
Game Blog

Nathan Heckman, Ba Choi, Yashesh Patel,
Chris English, Aaron Reyes
"""

import os
import flask
import requests
import socketio
from sqlalchemy import ForeignKey
import bcrypt
from flask import Flask, session, abort, redirect, render_template
from flask_socketio import SocketIO, send, emit
from oauth2client.contrib.flask_util import UserOAuth2
import google.oauth2.credentials
import google_auth_oauthlib.flow
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_login import (
    UserMixin,
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv, find_dotenv
from gamespot import get_game_article

from gamePlatform import get_game_platform


# from flask_bcrypt import Bcrypt


from igdb import (
    get_similar_games,
    search_game_data,
    get_cover_url,
    clean_string,
    get_game_data,
)


load_dotenv(find_dotenv())


app = flask.Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["BCRYPT_LEVEL"] = 10
socketio = SocketIO(app)

# bcrypt = Bcrypt(app)

# Point SQLAlchemy to your Heroku database
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["GOOGLE_OAUTH2_CLIENT_SECRETS_FILE"] = "client_secret.json"
# Point SQLAlchemy to Heroku database. Already accounted for postgres -> postgresql
app.config["SQLALCHEMY_DATABASE_URI"] = uri

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """
    This function queries the databse for the user ID of the current user
    """
    return Users.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """
    This function checks if a user is not logged in. If not they
    are redirected to the login page
    """
    return flask.redirect(flask.url_for("login"))


# socket io decorations


@socketio.on("message")
def handleMessage(msg):
    """
    This functions handles the sending of messages from a user to the chatroom
    """
    send("{.username}: ".format(current_user) + msg, broadcast=True)


@socketio.on("connect")
def test_connect():
    """
    This function handles connecting the user to the chatroom
    """
    send("Client connected: {.username}".format(current_user))


class Users(db.Model, UserMixin):
    """
    The table that holds the user's username and password
    """

    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique=True)
    password = db.Column(db.LargeBinary(), nullable=False)


class SaveGames(db.Model):
    """
    The table that holds username and it's associated saved games
    """

    __tablename__ = "SaveGames"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), ForeignKey("Users.username"))
    game_name = db.Column(db.String(), unique=True)

    def __repr__(self):
        return f"{self.game_name}"


db.create_all()
oauth2 = UserOAuth2(app)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This function handles all the login functionality for the app.
    This can be done using google oauth or a username and password protected
    by a secret key.
    """
    if oauth2.has_credentials():
        return flask.render_template(
            "main.html",
            username=oauth2.email,
            user_id=oauth2.user_id,
        )
    elif flask.request.method == "POST":
        user_form = flask.request.form
        if user_form["userName"] is None:
            flask.flash("Invalid User Information. Try Again!")
            return flask.render_template("login.html")

        elif Users.query.filter_by(username=user_form["userName"]).first():
            user_name = user_form["userName"]
            userPW = user_form["userPW"]
            user = Users.query.filter_by(username=user_name).first()
            userPW_hash = bcrypt.checkpw(userPW.encode("utf-8"), user.password)
            if userPW_hash:
                login_user(user)

                return flask.render_template("main.html", username=user.username)
            else:
                flask.flash("Invalid User Information. Try Again!")
                return flask.render_template("login.html")

        else:
            flask.flash("Invalid User Information. Try Again!")
            return flask.render_template("login.html")
    else:
        return flask.render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    This function displays the signup page. It allows new users to
    sign-up for an account if they do not want to use google oauth.
    All data is handled using a secret key and is stored in the database.
    """
    if flask.request.method == "POST":
        user_form = flask.request.form
        user_name = user_form["userName"]
        user_pw = user_form["userPW"]
        user_repw = user_form["userRePW"]
        isUN = Users.query.filter_by(username=user_form["userName"]).first()

        if not (user_name or user_pw or user_repw):
            flask.flash("All Blanks Must be Filled")
            return flask.redirect(flask.url_for("signup"))

        elif isUN:
            t = "The user name "
            y = " is already used. Try again!"
            flask.flash(t + user_name + y)  # already exist
            return flask.redirect(flask.url_for("signup"))

        elif len(user_pw) < 4:
            flask.flash(
                "Password Must be at Least 4 Digits. Try again!"
            )  # already exist
            return flask.redirect(flask.url_for("signup"))

        elif user_pw != user_repw:
            flask.flash("Passwords Must Match. Try again!")
            return flask.redirect(flask.url_for("signup"))

        else:
            user_pw_hash = bcrypt.hashpw(user_pw.encode("utf-8"), bcrypt.gensalt())
            user = Users(username=user_name, password=user_pw_hash)
            db.session.add(user)
            db.session.commit()
            x = "Sign Up Completed! Login with "
            flask.flash(x + user_name)
            return flask.redirect(flask.url_for("login"))
    return flask.render_template("signup.html")


@app.route("/logout")
def logout():
    """
    This function allows a user to logout of the app
    using flask session management
    """
    session.clear()
    return flask.redirect(flask.url_for("index"))


@app.route("/")
def index():
    """
    This function returns the base page of the app which
    has options to login or sign-up
    """
    return flask.render_template("index.html")


@app.route("/account")
def account():
    """
    This function gets the account html page and displays it
    """
    user = current_user.username
    saved_games = SaveGames.query.filter_by(username=user).all()
    return flask.render_template("account.html", username=user, saved_games=saved_games)


@app.route("/save_game", methods=["POST"])
def account_post():
    """
    This function saves a user inputted game into the database
    """
    data = flask.request.form
    game_name = data["game_name"]
    print(game_name)
    db_game_name = SaveGames.query.filter_by(game_name=game_name).first()
    print(db_game_name)
    if search_game_data(game_name) == "Invalid Name":
        flask.flash("Invalid game name. Try again!")
        return flask.redirect(flask.url_for("account"))
    if db_game_name:
        flask.flash("Game already saved. Try again!")
        return flask.redirect(flask.url_for("account"))

    game_commit = SaveGames(username=current_user.username, game_name=game_name)
    db.session.add(game_commit)
    db.session.commit()
    return flask.redirect(flask.url_for("account"))


@app.route("/del_game", methods=["POST"])
def account_delete():
    """
    This function deletes the game from a users saved list.
    """
    data = flask.request.form["game_name"]
    db_game_name = SaveGames.query.filter_by(game_name=data).first()
    db.session.delete(db_game_name)
    db.session.commit()
    return flask.redirect(flask.url_for("account"))


@app.route("/main", methods=["GET", "POST"])
def main():
    """
    This function handles the search requests and news api calls for the main page
    """
    user = current_user.username
    data = flask.request.form
    input_game = data["game"]
    if flask.request.method == "POST":
        if search_game_data(input_game) == "Invalid Name":
            flask.flash("Game does not exist or invalid name. Try again!")
        else:
            game_name, cover_url, game_summary = search_game_data(input_game)
            # This will be a 2D array with each subarray having 2 elements (name and cover url)
            similar_game_data = get_similar_games(input_game)

            return flask.render_template(
                "main.html",
                game_name=game_name,
                cover_url=cover_url,
                game_summary=game_summary,
                username=user,
                user_id=oauth2.user_id,
                similar_game_data=similar_game_data,
            )
    return flask.render_template(
        "main.html",
        username=user,
        user_id=oauth2.user_id,
    )


@app.route("/main2", methods=["GET", "POST"])
def main2():
    """
    This function returns the main page of the app. Here a user can search
    for a game and navigate to other pages in the app
    """
    user = current_user.username
    return flask.render_template("main.html", username=user)


@app.route("/NEWS", methods=["GET", "POST"])
def NEWS():
    """
    This function gets the news from the gamespot api and puts them in a list to be displayed
    """
    art_data = get_game_article()
    return flask.render_template(
        "NEWS.html",
        article1=art_data[0],
        article2=art_data[1],
        article3=art_data[2],
        article4=art_data[3],
        article5=art_data[4],
    )


@app.route("/gamePlatform", methods=["GET", "POST"])
def gamePlatform():
    """
    This function is used to select which platform the user wants news about.
    For example PC or Xbox.
    """
    data = flask.request.form
    platform = data["platform"]
    numbers = data["numbers"]
    game_data = get_game_platform(platform, numbers)

    return flask.render_template(
        "gamePlatform.html", game_data=game_data, page_num=int(numbers)
    )


@app.route("/oauth2authorize")
def oauth2authorize():
    """
    This function is used by ouath to authorize users
    """


@app.route("/oauth2callback")
def oauth2callback():
    """
    This function is used by ouath for callback to the original webpage
    """
    data = flask.request.form
    print(data)


@app.route("/chatroom", methods=["GET", "POST"])
def chatroom():
    """
    This function returns the page for the chatroom
    """
    user = current_user.username
    return flask.render_template("chatroom.html", username=user)


socketio.run(
    app,
    host=os.getenv("IP", "0.0.0.0"),
    port=int(os.getenv("PORT", 8080)),
    debug=True,
)
