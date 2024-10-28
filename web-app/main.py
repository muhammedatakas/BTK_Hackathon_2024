from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import re
import random  # For generating user_qid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # or your DB host
        user="root",
        password="147456Ata2073",
        database="mydb"
    )

# Home Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form['name']
        user_surname = request.form['surname']
        user_email = request.form['email']
        user_password = request.form['password']

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            flash("Invalid email address.")
            return redirect('/signup')

        # Validate password length
        if len(user_password) < 6:
            flash("Password should be at least 6 characters long.")
            return redirect('/signup')

        hashed_password = generate_password_hash(user_password)

        # Check if email already exists
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user WHERE user_email = %s', (user_email,))
        if cursor.fetchone():
            flash("Email already registered! Please log in.")
            return redirect('/login')

        # Insert new user
        user_qid = random.randint(0, 1800)
        cursor.execute('INSERT INTO user (user_name, user_surname, user_email, user_password, user_qid) VALUES (%s, %s, %s, %s, %s)',
                       (user_name, user_surname, user_email, hashed_password, user_qid))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Registration successful! Please log in.")
        return redirect('/login')

    return render_template('signup.html')

# Login Route with Error Handling
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Fetch the user by email
        cursor.execute('SELECT * FROM user WHERE user_email = %s', (user_email,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user and check_password_hash(user['user_password'], user_password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['user_name']
            return redirect('/')
        else:
            flash("Invalid email or password. Please try again.")
            return redirect('/login')

    return render_template('login.html')

# Home Route
@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html', user_name=session['user_name'])
    return redirect('/login')

# New Route for Displaying Categories and PDFs
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

# New Route to Display PDFs in a Selected Category
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

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run()