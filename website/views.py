import os
import uuid
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
    page = request.args.get('page', 1, type=int)
    per_page = 3  # Number of requests per page
    offset = (page - 1) * per_page

    cursor = mysql.connection.cursor()
    cursor.execute('SELECT COUNT(*) FROM adoption_request ar JOIN pets p ON ar.pet_id = p.id WHERE p.user_id = %s', (user_id,))
    total_requests = cursor.fetchone()[0]
    total_pages = (total_requests + per_page - 1) // per_page

    cursor.execute('''
        SELECT ar.message, ar.date_time, p.name AS pet_name, u.first_name, u.contact_no
        FROM adoption_request ar
        JOIN pets p ON ar.pet_id = p.id
        JOIN users u ON ar.user_id = u.id
        WHERE p.user_id = %s
        ORDER BY ar.date_time DESC
        LIMIT %s OFFSET %s
    ''', (user_id, per_page, offset))
    adoption_requests = cursor.fetchall()

    cursor.execute('SELECT * FROM pets WHERE user_id = %s', (user_id,))
    pets = cursor.fetchall()
    cursor.close()

    return render_template('dashboard.html', adoption_requests=adoption_requests, pets=pets, page=page, total_pages=total_pages, user=current_user)
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
            unique_filename = str(uuid.uuid4()) + filename
            upload_folder = os.path.join(current_app.root_path, 'static/images')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = os.path.join(upload_folder, unique_filename)
            image.save(image_path)
            image_url = url_for('static', filename=f'images/{unique_filename}')
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
        pet_images = [pet[11], pet[13], pet[14]]
        cursor.execute('SELECT * FROM users WHERE id = %s', (pet[12],))
        owner = cursor.fetchone()
        cursor.close()
    return render_template("adopt.html", pet = pet, owner = owner, pet_images = pet_images)


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
    pet_images = [pet[11], pet[13], pet[14]]
    cursor.close()

    return render_template("edit.html", pet=pet, pet_images=pet_images)

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
        # Handle image upload
    
        image1 = request.files['image1']
        image2 = request.files['image2']
        image3 = request.files['image3']
        images = [image1, image2, image3]

        #delte specific old images if new images are uploaded for that specific image   
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
        pet = cursor.fetchone()
        pet_images = [pet[11], pet[13], pet[14]]
        cursor.close()
        for i in range(0, 3):
            if images[i] and allowed_file(images[i].filename):
                if pet_images[i] != None:
                    cursor = mysql.connection.cursor()
                    #set the image column to null
                    if i == 0:
                        cursor.execute('UPDATE pets SET image_filename=NULL WHERE id=%s', (pet_id,))
                    elif i == 1:
                        cursor.execute('UPDATE pets SET img2=NULL WHERE id=%s', (pet_id,))
                    elif i == 2:
                        cursor.execute('UPDATE pets SET img3=NULL WHERE id=%s', (pet_id,))       
                    cursor.close()     
                    os.remove(os.path.join(current_app.root_path, pet_images[i][1:]))

        #upload new images
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                unique_filename = str(uuid.uuid4()) + filename
                upload_folder = os.path.join(current_app.root_path, 'static/images')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                image_path = os.path.join(upload_folder, unique_filename)
                image.save(image_path)
                image_url = url_for('static', filename=f'images/{unique_filename}')
                cursor = mysql.connection.cursor()
                if image == image1:
                    cursor.execute('UPDATE pets SET image_filename=%s WHERE id=%s', (image_url, pet_id))
                elif image == image2:
                    cursor.execute('UPDATE pets SET img2=%s WHERE id=%s', (image_url, pet_id))
                elif image == image3:
                    cursor.execute('UPDATE pets SET img3=%s WHERE id=%s', (image_url, pet_id))
                
                mysql.connection.commit()
                cursor.close()


        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE pets SET name=%s, age=%s, pet_type=%s, breed=%s, vaccinated=%s, city=%s, area=%s, sex=%s, neutered=%s, description=%s WHERE id=%s', (name, age, pet_type, breed, vax, city, area, sex, neutered, description, pet_id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('views.dashboard'))

@views.route('/delete/<int:pet_id>', methods=['POST'])
@login_required
def delete(pet_id):
    cursor = mysql.connection.cursor()
    #delete images from the server
    cursor.execute('SELECT * FROM pets WHERE id = %s', (pet_id,))
    pet = cursor.fetchone()
    pet_images = [pet[11], pet[13], pet[14]]
    cursor.close()
    for image in pet_images:
        if image != None:
            os.remove(os.path.join(current_app.root_path, image[1:]))
    cursor.execute('DELETE FROM pets WHERE id = %s', (pet_id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('views.dashboard'))
