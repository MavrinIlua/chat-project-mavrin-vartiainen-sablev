from flask import Flask, render_template, request # type: ignore

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    name = request.args.get("nickname")
    return f'{name}, приветствую!' 

@app.route("/about")

def about():
    return render_template("about.html")

app.run()
