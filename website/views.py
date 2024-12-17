from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import mysql

views = Blueprint('views', __name__)

@views.route('/')
def home():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM pets')
    pets = cursor.fetchall()
    cursor.close()
    return render_template('home.html', pets=pets)

@views.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")