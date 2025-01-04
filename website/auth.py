from flask import Blueprint, render_template, redirect, request, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQL
from . import mysql
from flask_login import login_user, login_required, logout_user, current_user
from .user import User

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            if check_password_hash(user[3], password):
                flash('Logged in successfully!', category='success')
                user_obj = User(id=user[0], email=user[1], first_name=user[2], password=user[3])

                login_user(user_obj, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName= request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        contact = request.form.get('contact')
        facebook = request.form.get('fb')
        whatsapp = request.form.get('whatsapp')
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()  
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash("Email must be greater than 4 characters", category='error')
        elif len(firstName) < 2:
            flash("First Name must be greater than 2 characters", category='error')
        elif password1 != password2:
            flash("Passwords don't match", category='error')
        elif len(password1) < 8:
            flash("Password must be at least 8 characters", category='error')   
        elif len(contact) != 11:
            flash("Contact must be 11 characters", category='error')
        else:
            cursor = mysql.connection.cursor()
            hashed_password = generate_password_hash(password1, method='pbkdf2:sha256')
            try:
                cursor.execute('INSERT INTO users (email, first_name, password, contact_no, facebook, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)', (email, firstName, hashed_password, contact, facebook, whatsapp))
                mysql.connection.commit()
                cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
                user = cursor.fetchone()
                cursor.close()
                user_obj = User(id=user[0], email=user[1], first_name=user[2], password=user[3])

                
                login_user(user_obj, remember=True)
                flash('Account created successfully!', category='success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                flash(f'Error: {str(e)}', category='error')
            finally:
                cursor.close()
         
    return render_template("sign_up.html", user=current_user)
