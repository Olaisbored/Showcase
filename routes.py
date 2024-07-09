from flask import render_template
from flask import current_app as app
from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='static')

    @app.route("/")
    def home_route():
        return render_template("home.html")

    return app