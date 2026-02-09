from flask import Flask, render_template
from database import get_all_sessions, init_db

app = Flask(__name__)

init_db() #ensures database exists

@app.route("/") #maps URL to this func, HTTP GET
def index():
	sessions = get_all_sessions()
	return render_template("index.html", sessions = sessions) #pass data to html

if __name__ == "__main__":
	app.run(host = "0.0.0.0", port = 5000, debug = True)

