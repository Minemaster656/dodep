from flask import Flask, Blueprint, request, render_template

app = Flask(__name__)
app.static_folder = "static"

@app.get("/")
def root():
    return render_template("index.html")

@app.get('/auth')
def auth_page():
    return render_template('pages/auth.html')