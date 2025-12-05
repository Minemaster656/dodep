from flask import Flask, Blueprint, request, render_template
from app.src.auth import auth
from app.src.work import work
from app.src.bank import bank
from app.src.casino import casino
from app.src.other import other
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET")
app.static_folder = "static"
app.register_blueprint(auth.bp)
app.register_blueprint(work.bp)
app.register_blueprint(bank.bp)
app.register_blueprint(casino.bp)
app.register_blueprint(other.bp)
app.register_blueprint(other.bp_nopref)


@app.get("/")
def root():
    return render_template("index.html")


@app.get('/auth')
def auth_page():
    return render_template('pages/auth.html')


@app.get('/readme')
def readme_page():
    return render_template('pages/readme.html')


@app.get('/work')
def work_page():
    return render_template('pages/work.html')


@app.get('/bank')
def bank_page():
    return render_template('pages/bank.html')


@app.get('/casino')
def casino_page():
    return render_template('pages/casino.html')

@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('pages/404.html')