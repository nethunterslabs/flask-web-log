from flask import Flask, request, Response
from flask_log import Log

app = Flask(__name__)
app.config["LOG_TYPE"] = "CSV"
Log(app)


@app.route('/', methods=["GET", "POST"])
def hello():
    return "lets test this log!"


if __name__ == '__main__':
    app.run(debug=True)
