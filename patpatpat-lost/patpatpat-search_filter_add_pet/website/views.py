from flask import Blueprint, app, render_template, request, redirect, url_for, jsonify, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import MySQLdb
from . import mysql

views = Blueprint('views', __name__)
from flask import g





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
    user_id = current_user.id
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT ar.message, ar.date_time, p.name AS pet_name
        FROM adoption_request ar
        JOIN pets p ON ar.pet_id = p.id
        WHERE p.user_id = %s
        ORDER BY ar.date_time DESC
    ''', (user_id,))
    adoption_requests = cursor.fetchall()
    cursor.execute('SELECT * FROM pets WHERE user_id = %s', (user_id,))
    pets = cursor.fetchall()
    cursor.close()
    return render_template("dashboard.html", user=current_user, adoption_requests=adoption_requests, pets=pets)
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

@views.route('/lost_found', methods=['GET'])
def lost_found():
    status = request.args.get('status')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if status=='found' or status=='lost':
        cursor.execute('SELECT id, name, breed, status, photo FROM lost_found WHERE status = %s', (status,))
    else:
        cursor.execute('SELECT id, name, breed, status, photo FROM lost_found')
    pets = cursor.fetchall()
    cursor.close()
    
    if request.is_json:
        return jsonify(pets)
    return render_template('lost_found.html', pets=pets)

@views.route('/confirm_lost_found', methods=['POST'])
def confirm_lost_found():
    pet_id = request.form['pet_id']
    message = request.form['message']
    
   
    return redirect(url_for('views.lost_found', pet_id=pet_id))




@views.route('/lost_found/<int:pet_id>', methods=['GET'])
def lost_found_details(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM lost_found WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    cursor.close()
    
    return render_template('lost_found_details.html', pet=pet)

@views.route('/adopt', methods=['GET', 'POST'])
@login_required
def adopt():
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
        pet = cursor.fetchone()
        cursor.close()
    return render_template("adopt.html", pet = pet)

@views.route('/claim/<int:pet_id>', methods=['GET', 'POST'])
def claim(pet_id):
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        message = request.form.get('message')
        
        return redirect(url_for('claim.html', pet_id=pet_id))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM lost_found WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    cursor.close()
    
    return render_template('claim.html', pet=pet)

@views.route('/confirm_adoption', methods=['GET', 'POST'])
def confirm_adoption():
    if request.method == 'POST':
        try:
            pet_id = request.form.get('pet_id')
            message = request.form.get('message')
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO adoption_request (pet_id, user_id, message) VALUES (%s, %s, %s)', (pet_id, current_user.id, message))
            mysql.connection.commit()
            cursor.close()
        except:
            flash("You've already requested this pet", category='error')    
    return redirect('/')

@views.route('/edit', methods=['POST'])
@login_required
def edit():
    pet_id = request.form.get('pet_id')
    print(pet_id)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    print(pet)
    cursor.close()

    return render_template("edit.html", pet=pet)

@views.route('/update/<int:pet_id>', methods=['POST'])
@login_required
def update(pet_id):
        name = request.form.get('name')
        city = request.form.get('location')
        area = request.form.get('area')
        pet_type = request.form.get('pet_type')
        breed = request.form.get('breed')
        age = request.form.get('age')
        sex = request.form.get('sex')
        vax = request.form.get('vaccinated') == '1'
        neutered = request.form.get('neutered') == '1'
        description = request.form.get('description')
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE pets SET name=%s, age=%s, pet_type=%s, breed=%s, vaccinated=%s, city=%s, area=%s, sex=%s, neutered=%s, description=%s WHERE id=%s', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, pet_id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('views.dashboard'))

@views.route('/delete/<int:pet_id>', methods=['POST'])
@login_required
def delete(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM pets WHERE id = %s', (pet_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('views.dashboard'))

@views.route('/claim_this_pet', methods=['GET', 'POST'])
def claim_pet():
    if request.method == 'POST':
        try:
            pet_id = request.form.get('pet_id')
            message = request.form.get('message')
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO claim_request (pet_id, user_id, message) VALUES (%s, %s, %s)', (pet_id, current_user.id, message))
            mysql.connection.commit()
            cursor.close()
        except:
            flash("You've already requested this pet", category='error')    
    return redirect('/')


