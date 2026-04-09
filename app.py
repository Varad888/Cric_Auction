
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/players")
def get_players():
    players_dir = os.path.join(app.static_folder, "players")
    players = [f for f in os.listdir(players_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    return players

if __name__ == "__main__":
    app.run(debug=True)
