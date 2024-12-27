import os
from flask import Blueprint, render_template, request, redirect, jsonify, url_for, current_app, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import mysql

views = Blueprint('views', __name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        vax = request.form.get('vaccinated') == '1'
        neutered = request.form.get('neutered') == '1'
        owner = current_user.id
        description = request.form.get('description')
        
        # Handle image upload
        image = request.files['photo']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/images')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            image_url = url_for('static', filename=f'images/{filename}')
        else:
            image_url = None

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO pets (name, age, pet_type, breed, vaccinated, city, area, sex, neutered, description, user_id, image_filename) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, owner, image_url))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('views.home'))

    return render_template("add.html")

@views.route('/adopt', methods=['GET', 'POST'])
@login_required
def adpot():
    if request.method == 'POST':
        pet_id = request.form.get('pet_id')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
        pet = cursor.fetchone()
        cursor.close()
    return render_template("adopt.html", pet = pet)


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
