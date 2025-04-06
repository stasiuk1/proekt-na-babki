
# Генерация сайта по расписанию
from app import api_create
from flask import Flask
app = Flask(__name__)

with app.app_context():
    api_create()
