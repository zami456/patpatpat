from flask import Blueprint, render_template, request
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

@views.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name')
        city = request.form.get('location')
        area = request.form.get('area')
        pet_type = request.form.get('pet_type')
        breed = request.form.get('breed')
        age = request.form.get('age')
        sex = request.form.get('sex')
        vax = request.form.get('vaccinated') == '1'
        neutered = request.form.get('neutered') == '1'
        owner = current_user.id
        description = request.form.get('description')
        print(name, age, breed, vax, city, area, description, owner)
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO pets (name, age, pet_type, breed, vaccinated, city, area, sex, neutered, description, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, owner))
        mysql.connection.commit()
        cursor.close()
    

    return render_template("add.html")