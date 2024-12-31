from flask import Blueprint, render_template, request, redirect, jsonify
from flask_login import login_required, current_user
from . import mysql

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        city = request.form.get('city')
        area = request.form.get('area')
        pet_type = request.form.get('pet_type')
        age = request.form.get('age')
        vaccinated = request.form.get('vaccinated')
        sex = request.form.get('sex')
        neutered = request.form.get('neutered')
        search = request.form.get('search')

        query = 'SELECT * FROM pets WHERE 1=1'
        params = []

        if city:
            query += ' AND city = %s'
            params.append(city)
        if area:
            query += ' AND area = %s'
            params.append(area)
        if pet_type:
            query += ' AND pet_type = %s'
            params.append(pet_type)
        if age:
            query += ' AND age = %s'
            params.append(age)
        if vaccinated:
            query += ' AND vaccinated = %s'
            params.append(vaccinated)
        if sex:
            query += ' AND sex = %s'
            params.append(sex)
        if neutered:
            query += ' AND neutered = %s'
            params.append(neutered)
        if search:
            query += ' AND (name LIKE %s OR breed LIKE %s OR description LIKE %s)'
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        cursor = mysql.connection.cursor()
        cursor.execute(query, params)
        pets = cursor.fetchall()
        cursor.close()

        # Return JSON response for AJAX request
        return jsonify({'pets': pets})

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
        status=request.form.get('status')
        vax = request.form.get('vaccinated') == '1'
        neutered = request.form.get('neutered') == '1'
        owner = current_user.id
        description = request.form.get('description')
        print(name, age, breed, vax, city, area, description, owner)
        print(status,1)
        cursor=mysql.connection.cursor()
        if status=='found' or status=='lost':
            cursor.execute('INSERT INTO lost_found (name,location) VALUES ( %s, %s)' , (name,city)) 
        else:
            cursor.execute('INSERT INTO pets (name, age, pet_type, breed, vaccinated, city, area, sex, neutered, description, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, owner))
        mysql.connection.commit()
        cursor.close()
    

    return render_template("add.html")
@views.route('/lost_found', methods=['GET', 'POST'])
def lost_found():
    if request.method=='GET':
        cursor=mysql.connection.cursor()
        cursor.execute('SELECT * FROM lost_found')
        pets=cursor.fetchall()
        cursor.close()
        return render_template("lost_found.html",pets=pets)
    return render_template("lost_found.html")





