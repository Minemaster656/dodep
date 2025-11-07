from flask import Flask, Blueprint, request, render_template
from app.src.auth import auth
app = Flask(__name__)
app.static_folder = "static"
app.register_blueprint(auth.bp)
@app.get("/")
def root():
    return render_template("index.html")

@app.get('/auth')
def auth_page():
    return render_template('pages/auth.html')