from flask import Flask
from main import app

@app.route('/')
def landing():
    return "Test"