from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Specify upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)  # Create the folder if it doesn't exist

# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # or your DB host
        user="root",
        password="",
        database="mydb"
    )

# Home Route
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html', user_name=session['user_name'])
    return redirect('/login')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch the user by email
        cursor.execute('SELECT * FROM User WHERE user_email = %s', (user_email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['user_password'], user_password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['user_name']
            return redirect('/')
        else:
            flash("Invalid email or password. Please try again.")
    
    return render_template('login.html')

# Sign-up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['name']
        user_surname = request.form['surname']
        user_email = request.form['email']
        user_password = request.form['password']

        # Basic form validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            flash("Invalid email address")
            return render_template('signup.html')

        if len(user_password) < 6:
            flash("Password should be at least 6 characters long")
            return render_template('signup.html')

        # Hash the password
        hashed_password = generate_password_hash(user_password)

        # Insert user into database
        connection = get_db_connection()
        cursor = connection.cursor()

        # Check if email already exists
        cursor.execute('SELECT * FROM User WHERE user_email = %s', (user_email,))
        account = cursor.fetchone()
        if account:
            flash("Email already registered! Please log in.")
            return redirect('/login')

        # Generate a unique user_qid
        user_qid = random.randint(0, 1800)
        user_id = user_qid

        # Insert new user into the User table
        cursor.execute('INSERT INTO User (user_id, user_name, user_surname, user_email, user_password, user_qid) VALUES (%s, %s, %s, %s, %s, %s)',
                       (user_id, user_name, user_surname, user_email, hashed_password, user_qid))
        connection.commit()

        flash("Registration successful! Please log in.")
        return redirect('/login')
    
    return render_template('signup.html')

# **New Route for Displaying Categories and PDFs**
@app.route('/categories')
def categories():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch distinct categories for the logged-in user
    cursor.execute('SELECT DISTINCT pdf_category FROM user_data WHERE user_id = %s', (user_id,))
    categories = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('categories.html', categories=categories)

# **New Route to Display PDFs in a Selected Category**
@app.route('/pdfs/<category>')
def pdf_list(category):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch all PDFs for the selected category
    cursor.execute('SELECT pdf_name FROM user_data WHERE user_id = %s AND pdf_category = %s', (user_id, category))
    pdfs = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('pdfs.html', pdfs=pdfs, category=category)

# **New Route for Uploading PDFs**
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        user_id = session['user_id']
        pdf_file = request.files['pdf_file']
        pdf_category = request.form['pdf_category']

        # Check if the file is a PDF
        if not pdf_file or not pdf_file.filename.endswith('.pdf'):
            flash("Please upload a valid PDF file.")
            return redirect('/upload')

        # Save the PDF file
        pdf_filename = pdf_file.filename
        pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))

        # Insert PDF data into the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('INSERT INTO user_data (user_id, pdf_name, pdf_category) VALUES (%s, %s, %s)',
                       (user_id, pdf_filename, pdf_category))
        connection.commit()
        cursor.close()
        connection.close()

        flash("PDF uploaded successfully!")
        return redirect('/categories')

    return render_template('upload.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run()
