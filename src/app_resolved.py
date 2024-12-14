import identity.web
import requests
import os
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
import secrets

# The following variables are required for the app to run.

# TODO: Use the Azure portal to register your application and generate client id and secret credentials.
CLIENT_ID = "some id"
CLIENT_SECRET = "some secret"

# TODO: Figure out your authentication authority id.
AUTHORITY = "some authority"

# TODO: generate a secret. Used by flask session for protecting cookies.
secret_key = secrets.token_hex(16)
SESSION_SECRET = secret_key

# TODO: Figure out what scopes you need to use
SCOPES = ["User.Read", "User.ReadWrite", "User.ReadBasic.All"]

# TODO: Figure out the URI where Azure will redirect to after authentication. After deployment, this should
#  be on your server. The URI must match one you have configured in your application registration.
REDIRECT_URI = "https://pro028.x310.net/getAToken"

REDIRECT_PATH = "/getAToken"

app = Flask(__name__)

app.config['SECRET_KEY'] = SESSION_SECRET
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TESTING'] = True
app.config['DEBUG'] = True
Session(app)

# The auth object provide methods for interacting with the Microsoft OpenID service.
auth = identity.web.Auth(session=session,
                         authority=AUTHORITY,
                         client_id=CLIENT_ID,
                         client_credential=CLIENT_SECRET)

@app.route("/login")
def login():
    # TODO: Use the auth object to log in.
    return render_template("login.html", **auth.log_in(
        scopes=SCOPES,
        redirect_uri=url_for("auth_response", _external=True),
    ))


@app.route(REDIRECT_PATH)
def auth_response():
    # TODO: Use the flask request object and auth object to complete the authentication.
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    # TODO: Use the auth object to log out and redirect to the home page
    return redirect(auth.log_out(url_for("index", _external=True)))


@app.route("/")
def index():
    # TODO: use the auth object to get the profile of the logged in user.
    if not auth.get_user():
        return redirect(url_for("login"))
    print(auth.get_user())
    return render_template('index.html', user=auth.get_user())


@app.route("/profile", methods=["GET"])
def get_profile():
    # TODO: Check that the user is loggen in and add credentials to the http request.
    access_token = auth.get_token_for_user(SCOPES)
    if "error" in access_token:
        return render_template('auth_error.html', result=access_token)
    user_data = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + access_token["access_token"]},
        timeout=30,
    ).json()
    return render_template('profile.html', user=user_data, result=user_data)


@app.route("/profile", methods=["POST"])
def post_profile():
    access_token = auth.get_token_for_user(SCOPES)
    if "error" in access_token:
        return render_template('auth_error.html', result=access_token)
    # TODO: check that the user is logged in and add credentials to the http request.
    result = requests.patch(
        'https://graph.microsoft.com/v1.0/users/' + request.form.get("id"),
        json=request.form.to_dict(),
        headers={'Authorization': 'Bearer ' + access_token["access_token"]},
        timeout=30,
    )

    # TODO: add credentials to the http request.
    profile = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': 'Bearer ' + access_token["access_token"]},
        timeout=30,

    )
    return render_template('profile.html',
                           user=profile.json(),
                           result=result)


@app.route("/users")
def get_users():

    # TODO: Check that user is logged in and add credentials to the request.
    access_token = auth.get_token_for_user(SCOPES)
    if "error" in access_token:
        return render_template('auth_error.html', result=access_token)
    result = requests.get(
        'https://graph.microsoft.com/v1.0/users',
        headers={'Authorization': 'Bearer ' + access_token["access_token"]},
        timeout=30,
    )
    return render_template('users.html', result=result.json())


if __name__ == "__main__":
    app.run()
