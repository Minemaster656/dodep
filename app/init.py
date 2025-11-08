from flask import Flask, Blueprint, request, render_template
from app.src.auth import auth
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET")
app.static_folder = "static"
app.register_blueprint(auth.bp)
@app.get("/")
def root():
    return render_template("index.html")

@app.get('/auth')
def auth_page():
    return render_template('pages/auth.html')
@app.get('/readme')
def readme_page():
    return render_template('pages/readme.html')