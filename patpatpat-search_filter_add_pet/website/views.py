from flask import Blueprint, app, render_template, request, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import MySQLdb
from . import mysql

views = Blueprint('views', __name__)
from flask import g

# Use MySQLdb's DictCursor to fetch results as dictionaries
cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        pet_type = request.form.get('pet_type')
        breed = request.form.get('breed')
        vax = request.form.get('vaccinated')
        city = request.form.get('city')
        area = request.form.get('area')
        sex = request.form.get('sex')
        neutered = request.form.get('neutered')
        description = request.form.get('description')
        owner = request.form.get('owner')
        status = request.form.get('status')
        
        # Handle file upload
        photo = request.files['photo']
        if photo:
            filename = secure_filename(photo.filename)
            with current_app.app_context():
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                photo_url = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        cursor = mysql.connection.cursor()
        if status == 'found' or status == 'lost':
            cursor.execute('INSERT INTO lost_found (name, location, photo, status) VALUES (%s, %s, %s, %s)', (name, city, photo_url, status))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('views.lost_found', status=status))
        else:
            cursor.execute('INSERT INTO pets (name, age, pet_type, breed, vaccinated, city, area, sex, neutered, description, user_id, photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, owner, photo_url))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('views.home'))
    return render_template('add.html')

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

@views.route('/lost_found', methods=['GET'])
def lost_found():
    status = request.args.get('status')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if status:
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
    
    # Process the message and update the pet's status or handle accordingly
    # For example, storing the message in a database, or notifying the owner
    
    # Redirect to a confirmation or pet details page
    return redirect(url_for('views.lost_found', pet_id=pet_id))

# Manually push the app context if you're outside the request context


@views.route('/lost_found/<int:pet_id>', methods=['GET'])
def lost_found_details(pet_id):
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM lost_found WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    cursor.close()
    
    return render_template('lost_found_details.html', pet=pet)



