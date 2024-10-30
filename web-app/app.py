# APP.PY

import streamlit as st
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from prompt_template import QuestionGenerator
from summarizer import create_summary
from pdf_reader import get_pdf_content
from summarizer import create_summary
from database import Database
import re

# Initialize Database
db = Database()

# Initialize Streamlit app
st.set_page_config(page_title="Interactive Question Generation App", layout="wide")
st.title("Interactive Question Generation App")

# User Authentication State
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""

# Authentication Functions
def authenticate_user(email, password):
    """Authenticate user and return user details if valid."""
    print(f"Authenticating user with email: {email}")
    user = db.get_user_by_email(email)
    if user and check_password_hash(user['user_password'], password):
        st.session_state['user_id'] = user['user_id']
        st.session_state['user_name'] = user['user_name']
        print(f"User authenticated: {user['user_name']} (ID: {user['user_id']})")
        return True
    else:
        print("Authentication failed.")
        return False

def register_user(name, surname, email, password):
    """Register a new user after checking for existing email."""
    print(f"Registering user: {name} {surname}, Email: {email}")
    if db.get_user_by_email(email):
        st.error("Email already registered! Please log in.")
        print("Registration failed: Email already exists.")
        return False
    hashed_password = generate_password_hash(password)
    db.insert_user(None, name, surname, email, hashed_password)  # Assuming user_id is auto-incremented
    print("User registered successfully.")
    return True

def login_page():
    st.header("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if authenticate_user(email, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password.")

def signup_page():
    st.header("Sign Up")
    name = st.text_input("First Name")
    surname = st.text_input("Last Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            st.error("Invalid email address.")
            print("Signup failed: Invalid email format.")
        elif len(password) < 6:
            st.error("Password should be at least 6 characters long.")
            print("Signup failed: Password too short.")
        elif register_user(name, surname, email, password):
            st.success("Registration successful! Please log in.")
        else:
            st.error("Failed to register. Try again.")

def upload_pdf_page():
    st.header("Upload PDF")
    user_id = st.session_state['user_id']
    folder_name = st.text_input("Folder Name")
    pdf_files = st.file_uploader("Upload PDFs (Max 5)", type="pdf", accept_multiple_files=True)
    
    if st.button("Upload PDFs"):
        print(f"Uploading PDFs for user_id: {user_id}, Folder: {folder_name}")
        if not folder_name:
            st.error("Folder name is required.")
            print("Upload failed: Folder name missing.")
            return
        if not pdf_files:
            st.error("Please select at least one PDF file.")
            print("Upload failed: No files selected.")
            return
        if len(pdf_files) > 5:
            st.error("You can upload a maximum of 5 PDFs at a time.")
            print("Upload failed: Exceeded file limit.")
            return
        
        user_folder = os.path.join('static/uploads', str(user_id), folder_name)
        os.makedirs(user_folder, exist_ok=True)
        print(f"User folder created at: {user_folder}")
        
        uploaded_count = 0
        for pdf_file in pdf_files:
            if uploaded_count >= 5:
                st.warning("Reached the maximum upload limit of 5 PDFs.")
                print("Upload stopped: Maximum limit reached.")
                break
            filename = secure_filename(pdf_file.name)
            pdf_path = os.path.join(user_folder, filename)
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            print(f"Uploaded PDF: {pdf_path}")
            summary = create_summary(get_pdf_content(pdf_path=pdf_path))
            print(f"Generated summary for {filename}: {summary}")
            try:
                db.insert_summary(user_id, filename, folder_name, summary)
                uploaded_count += 1
            except Exception as e:
                st.error(f"Error uploading PDF '{filename}': {e}")
                print(f"Error uploading PDF '{filename}': {e}")
        
        st.success(f"Successfully uploaded {uploaded_count} PDF(s).")
        print(f"Total PDFs uploaded: {uploaded_count}")

def generate_questions_page():
    st.header("Generate Questions")
    user_id = st.session_state['user_id']
    files = db.get_user_pdf_data(user_id)
    print(f"Generating questions for user_id: {user_id}, Files: {files}")
    
    if not files:
        st.info("No PDFs uploaded yet. Please upload PDFs first.")
        print("No PDFs found for question generation.")
        return

    pdf_names = [file['pdf_name'] for file in files]
    selected_pdfs = st.multiselect("Select PDFs (up to 3)", pdf_names, max_selections=3)
    difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
    quantity = st.slider("Number of Questions per PDF", 1, 20, 5)
    
    if st.button("Generate Questions"):
        print(f"Generating {quantity} questions per PDF with difficulty '{difficulty}'")
        if not selected_pdfs:
            st.error("Please select at least one PDF.")
            print("Question generation failed: No PDFs selected.")
            return
        
        q_gen = QuestionGenerator(api_key=os.getenv('API_KEY'), db_instance=db)
        generated_questions = []
        
        for pdf_name in selected_pdfs:
            try:
                pdf_data = next((f for f in files if f['pdf_name'] == pdf_name), None)
                if not pdf_data:
                    st.error(f"PDF '{pdf_name}' not found.")
                    print(f"PDF '{pdf_name}' data not found.")
                    continue
                
                for _ in range(quantity):
                    question_data = q_gen.generate_questions_from_summary(
                        pdf_name, pdf_data['pdf_summary'], pdf_data['pdf_category'], difficulty
                    )
                    if question_data:
                        db.insert_user_question(user_id, question_data)
                        generated_questions.append(question_data)
                        print(f"Generated question: {question_data['q_title']}")
            except Exception as e:
                st.error(f"Error generating questions for '{pdf_name}': {e}")
                print(f"Error generating questions for '{pdf_name}': {e}")
        
        if generated_questions:
            st.session_state['generated_questions'] = generated_questions
            st.success(f"Generated {len(generated_questions)} questions successfully!")
            print(f"Total questions generated: {len(generated_questions)}")
            st.rerun()
        else:
            st.error("No questions were generated. Please try again.")
            print("No questions were generated.")

def view_questions_page():
    st.header("View Generated Questions")
    generated_questions = db.get_user_questions(st.session_state['user_id'])
    print(f"Viewing questions for user_id: {st.session_state['user_id']}, Questions: {generated_questions}")
    if not generated_questions:
        st.info("No questions generated yet.")
        print("No questions found.")
        return
    
    for idx, question in enumerate(generated_questions, start=1):
        with st.expander(f"Question {idx}: {question['q_title']}"):
            st.write(f"**Topic:** {question['q_topic']}")
            st.write(f"A. {question['qA']}")
            st.write(f"B. {question['qB']}")
            st.write(f"C. {question['qC']}")
            st.write(f"D. {question['qD']}")
            if st.button("Show Answer", key=f"answer_{idx}"):
                st.write(f"**Answer:** {question['qra']}")
                st.write(f"**Explanation:** {question['qex']}")
                print(f"Displayed answer for question {idx}.")

# Sidebar Navigation
if st.session_state['user_id']:
    st.sidebar.title(f"Welcome, {st.session_state['user_name']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully.")
        print("User logged out.")
        st.rerun()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["Upload PDF", "Generate Questions", "View Questions"])
else:
    st.sidebar.header("Authentication")
    auth_option = st.sidebar.radio("Choose Option", ["Login", "Sign Up"])
    if auth_option == "Login":
        login_page()
    else:
        signup_page()

# Main Page Content
if st.session_state['user_id']:
    if page == "Upload PDF":
        upload_pdf_page()
    elif page == "Generate Questions":
        generate_questions_page()
    elif page == "View Questions":
        view_questions_page()

# Close Database Connection on App Exit
def on_exit():
    print("Closing database connection.")
    db.close()

import atexit
atexit.register(on_exit)