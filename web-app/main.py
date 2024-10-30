from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re
from summarizer import create_summary
from prompt_template import QuestionGenerator, get_user_pdf_data, store_user_question, connect_to_database  # Import your question generator code
from pdf_reader import get_pdf_content

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Update the upload folder path
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# MySQL Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # or your DB host
        user="root",
        password="147456Ata2073",
        database="mydb"
    )

api_key = os.getenv('API_KEY')
if not api_key:
    print("API Key not found. Please set the environment variable.")
    exit()
db_connection = connect_to_database()

# Render the Question Generation Page
@app.route('/generate_questions', methods=['GET'])
def generate_questions_page():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    files = get_user_pdf_data(db_connection, user_id)
    return render_template('generate_questions.html', files=files)

# Process Question Generation

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
        cursor.execute('INSERT INTO user (user_name, user_surname, user_email, user_password) VALUES (%s, %s, %s, %s)',
                       (user_name, user_surname, user_email, hashed_password))
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
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch distinct folder names and files associated with the user
    cursor.execute('SELECT DISTINCT pdf_category FROM user_data WHERE user_id = %s', (user_id,))
    folders = cursor.fetchall()
    
    cursor.execute('SELECT pdf_name, pdf_category FROM user_data WHERE user_id = %s', (user_id,))
    files = cursor.fetchall()

    cursor.close()
    connection.close()
    
    return render_template('home.html', folders=folders, files=files)

# Upload PDF Route with folder/category support
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    folder_name = request.form['folder_name']
    pdf_file = request.files['pdf_file']

    if pdf_file and folder_name:
        filename = secure_filename(pdf_file.filename)
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), folder_name)
        os.makedirs(user_folder, exist_ok=True)
        pdf_path = os.path.join(user_folder, filename)
        pdf_file.save(pdf_path)

        # Save to database with folder as the pdf_category
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO user_data (user_id, pdf_name, pdf_category, pdf_path) VALUES (%s, %s, %s, %s)',
            (user_id, filename, folder_name, pdf_path)
        )
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("File uploaded successfully!")
    else:
        flash("Failed to upload the file. Please try again.")
    
    return redirect('/')

# Generate Questions Route
@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    selected_pdfs = request.form.getlist('pdf_selection')
    difficulty = request.form.get('difficulty', 'Medium')
    quantity = int(request.form.get('quantity', 5))

    connection = get_db_connection()
    q_gen = QuestionGenerator(api_key=os.getenv('API_KEY'), db_connection=connection)

    generated_questions = []
    for pdf_name in selected_pdfs[:3]:  # Limit to 3 PDFs
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            'SELECT pdf_summary, pdf_category FROM user_data WHERE user_id = %s AND pdf_name = %s',
            (user_id, pdf_name)
        )
        pdf_data = cursor.fetchone()
        cursor.fetchall()  # Fetch all remaining results to avoid unread result error
        cursor.close()
        if not pdf_data:
            flash(f"PDF '{pdf_name}' not found.")
            continue
        
        for _ in range(quantity):
            question_data = q_gen.generate_questions_from_summary(
                pdf_name=pdf_name,
                pdf_summary=pdf_data['pdf_summary'],
                pdf_category=pdf_data['pdf_category'],
                difficulty=difficulty
            )
            if question_data and q_gen.validate_question_data(question_data):
                store_user_question(connection, question_data, user_id)
                generated_questions.append(question_data)

    connection.close()
    return render_template('question_results.html', questions=generated_questions)


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