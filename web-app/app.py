# APP.PY

import streamlit as st
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from prompt_template import QuestionGenerator,AIAssistant
from summarizer import create_summary
from pdf_reader import get_pdf_content
from summarizer import create_summary
from database import Database
import re
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd

# Initialize Database
db = Database()

# Initialize Streamlit app
st.set_page_config(page_title="Interactive Question Generation App", layout="wide")
st.title("Interactive Question Generation App")

q_gen = QuestionGenerator(api_key=os.getenv('API_KEY'), db_instance=db)
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
    st.header("PDF Management")
    user_id = st.session_state['user_id']

    # Create tabs for Upload and Manage
    tab1, tab2 = st.tabs(["Upload PDFs", "Manage PDFs"])

    with tab1:
        folder_name = st.text_input("Folder Name")
        pdf_files = st.file_uploader("Upload PDFs (Max 5)", type="pdf", accept_multiple_files=True)
        
        if st.button("Upload PDFs"):
            if not folder_name:
                st.error("Folder name is required.")
                return
            if not pdf_files:
                st.error("Please select at least one PDF file.")
                return
            if len(pdf_files) > 5:
                st.error("You can upload a maximum of 5 PDFs at a time.")
                return
            
            user_folder = os.path.join('static/uploads', str(user_id), folder_name)
            os.makedirs(user_folder, exist_ok=True)
            
            uploaded_count = 0
            for pdf_file in pdf_files:
                if uploaded_count >= 5:
                    st.warning("Reached the maximum upload limit of 5 PDFs.")
                    break
                filename = secure_filename(pdf_file.name)
                pdf_path = os.path.join(user_folder, filename)
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                summary = create_summary(get_pdf_content(pdf_path=pdf_path))
                try:
                    db.insert_summary(user_id, filename, folder_name, summary)
                    uploaded_count += 1
                except Exception as e:
                    st.error(f"Error uploading PDF '{filename}': {e}")
            
            st.success(f"Successfully uploaded {uploaded_count} PDF(s).")

    with tab2:
        st.subheader("Manage Existing PDFs")
        
        # Get all PDFs for the user
        pdfs = db.get_user_pdf_data(user_id)
        if not pdfs:
            st.info("No PDFs uploaded yet.")
            return

        # Group PDFs by category/folder
        pdf_by_category = {}
        for pdf in pdfs:
            category = pdf['pdf_category']
            if category not in pdf_by_category:
                pdf_by_category[category] = []
            pdf_by_category[category].append(pdf)

        # Display PDFs by category with delete options
        for category, category_pdfs in pdf_by_category.items():
            with st.expander(f"📁 {category}"):
                # Add delete category button
                if st.button(f"Delete Category: {category}", key=f"del_cat_{category}"):
                    try:
                        db.delete_category(user_id, category)
                        # Remove folder
                        folder_path = os.path.join('static/uploads', str(user_id), category)
                        if os.path.exists(folder_path):
                            import shutil
                            shutil.rmtree(folder_path)
                        st.success(f"Category '{category}' deleted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error deleting category: {e}")

                # List PDFs in category
                for pdf in category_pdfs:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📄 {pdf['pdf_name']}")
                    with col2:
                        if st.button("Delete", key=f"del_{pdf['pdf_name']}"):
                            try:
                                db.delete_pdf(user_id, pdf['pdf_name'])
                                # Remove file
                                pdf_path = os.path.join('static/uploads', str(user_id), category, pdf['pdf_name'])
                                if os.path.exists(pdf_path):
                                    os.remove(pdf_path)
                                st.success(f"PDF '{pdf['pdf_name']}' deleted successfully.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting PDF: {e}")


import streamlit as st
import os

def generate_questions_page():
    if 'generated_questions' in st.session_state:
        display_questions()
    else:
        st.header("Generate Questions")
        user_id = st.session_state['user_id']
        files = db.get_user_pdf_data(user_id)
        
        if not files:
            st.info("No PDFs uploaded yet. Please upload PDFs first.")
            return

        # Selection interface
        selected_topic = st.selectbox("Select Topic", ["All"] + [val["pdf_category"] for val in db.get_user_categories(user_id)])
        pdf_names = [file['pdf_name'] for file in files if file['pdf_category'] == selected_topic or selected_topic == "All"]
        selected_pdfs = st.multiselect("Select PDFs (up to 3)", pdf_names, max_selections=3)
        difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
        quantity = st.slider("Number of Questions per PDF", 1, 20, 5)

        if st.button("Generate Questions"):
            if not selected_pdfs:
                st.error("Please select at least one PDF.")
                return

            generated_questions = []
            with st.spinner("Generating questions..."):
                for pdf_name in selected_pdfs:
                    pdf_data = next((f for f in files if f['pdf_name'] == pdf_name), None)
                    if pdf_data:
                        for _ in range(quantity):
                            question_data = q_gen.generate_questions_from_summary(
                                pdf_name, pdf_data['pdf_summary'], pdf_data['pdf_category'], difficulty
                            )
                            if question_data:
                                generated_questions.append(question_data)

            if generated_questions:
                st.session_state['generated_questions'] = generated_questions
                st.success(f"Generated {len(generated_questions)} questions successfully!")
                st.rerun()

def display_questions():
    if 'generated_questions' not in st.session_state:
        st.error("No questions available. Generate questions first.")
        return

    st.header("Answer Questions")
    generated_questions = st.session_state['generated_questions']
    user_id = st.session_state['user_id']

    # Initialize user_answers if not present
    if 'user_answers' not in st.session_state:
        st.session_state['user_answers'] = {}

    # Display questions and collect answers
    for idx, question in enumerate(generated_questions):
        st.subheader(f"Question {idx + 1}")
        st.write(question['q_title'])

        # Create options dictionary
        options = {
            'A': question['opt_a'],
            'B': question['opt_b'],
            'C': question['opt_c'],
            'D': question['opt_d']
        }
        
        # Display options with labels
        selected_option = st.radio(
            "Select your answer:",
            options=['A', 'B', 'C', 'D'],
            format_func=lambda x: f"{x}: {options[x]}",
            key=f"q_{idx}",
            index=None
        )
        
        if selected_option:
            st.session_state['user_answers'][idx] = selected_option

    # Submit button
    if st.button("Submit Answers"):
        if len(st.session_state['user_answers']) != len(generated_questions):
            st.error("Please answer all questions before submitting.")
            return

        score = 0
        submitted_questions = 0
        
        try:
            for idx, question in enumerate(generated_questions):
                user_answer = st.session_state['user_answers'].get(idx)
                
                # Prepare question data for database
                question_data = {
                    'q_topic': question['q_topic'],
                    'q_title': question['q_title'],
                    'opt_a': question['opt_a'],
                    'opt_b': question['opt_b'],
                    'opt_c': question['opt_c'],
                    'opt_d': question['opt_d'],
                    'answer': question['answer'],  # This is qra
                    'qua': user_answer,
                    'explanation': question['explanation'],
                    'difficulty': question.get('difficulty', 'Medium')
                }

                try:
                    # Insert into database with proper field mapping
                    db.insert_user_question(user_id, {
                        'q_topic': question_data['q_topic'],
                        'q_title': question_data['q_title'],
                        'opt_a': question_data['opt_a'],
                        'opt_b': question_data['opt_b'],
                        'opt_c': question_data['opt_c'],
                        'opt_d': question_data['opt_d'],
                        'qra': question_data['answer'],
                        'qua': question_data['qua'],
                        'qex': question_data['explanation'],
                        'qdiff': question_data['difficulty']
                    })
                    
                    submitted_questions += 1
                    if user_answer == question['answer']:
                        score += 1
                        
                except Exception as e:
                    print(f"Error inserting question {idx + 1}: {e}")
                    continue

            if submitted_questions > 0:
                st.success(f"Score: {score}/{submitted_questions} ({(score/submitted_questions)*100:.1f}%)")
                
                # Show explanations
                for idx, question in enumerate(generated_questions):
                    with st.expander(f"Question {idx + 1} Explanation"):
                        user_answer = st.session_state['user_answers'].get(idx)
                        st.write(f"Your answer: {user_answer}")
                        st.write(f"Correct answer: {question['answer']}")
                        st.write(f"Explanation: {question['explanation']}")
                
                # Add Generate Again button
                if st.button("Generate New Questions"):
                    del st.session_state['generated_questions']
                    del st.session_state['user_answers']
                    st.rerun()
            else:
                st.error("Failed to submit any questions. Please try again.")

        except Exception as e:
            st.error(f"Error submitting answers: {str(e)}")
            print(f"Error details: {e}")

            
            
# Update the analyze_questions_page function in APP.PY

def analyze_questions_page():
    st.header("Question Analysis Dashboard")
    user_id = st.session_state['user_id']
    
    # Initialize AI Assistant
    ai_assistant = AIAssistant(api_key=os.getenv('API_KEY'))

    # Sidebar filters
    with st.sidebar:
        st.subheader("Filters")
        
        date_range = st.date_input(
            "Select Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now())
        )
        
        topics = db.get_user_categories(user_id)
        selected_topics = st.multiselect(
            "Select Topics",
            options=[topic['pdf_category'] for topic in topics]
        )
        
        difficulty = st.selectbox(
            "Difficulty Level",
            ["All", "Easy", "Medium", "Hard"]
        )

    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        analytics = db.get_user_question_analytics(user_id)
        if analytics:
            # Performance Overview
            st.subheader("Performance Overview")
            fig1 = create_performance_chart(analytics)
            st.plotly_chart(fig1, use_container_width=True, key="performance_chart")
            
            # Topic Mastery Heatmap
            st.subheader("Topic Mastery Heatmap")
            fig2 = create_mastery_heatmap(analytics)
            st.plotly_chart(fig2, use_container_width=True, key="mastery_heatmap")
        else:
            st.info("No analytics data available yet. Complete some questions to see your performance.")

    with col2:
        st.subheader("Learning Insights")
        if analytics:
            # Quick Stats
            total_questions = sum(topic['total_questions'] for topic in analytics)
            total_correct = sum(topic['correct_answers'] for topic in analytics)
            
            if total_questions > 0:
                accuracy = (total_correct/total_questions)*100
                st.metric("Questions Attempted", total_questions)
                st.metric("Overall Accuracy", f"{accuracy:.1f}%")
            
                # Topic Recommendations
                recommendations = db.get_topic_recommendations(user_id)
                if recommendations:
                    st.subheader("Recommended Focus Areas")
                    for rec in recommendations:
                        st.warning(f"📚 {rec['q_topic']} (Mastery: {rec['avg_mastery']:.1f}%)")
        else:
            st.info("Complete some questions to see your insights.")

    # Question Review Tabs
    st.subheader("Question Review")
    tabs = st.tabs(["All Questions", "Incorrect Answers", "By Topic"])
    
    filtered_questions = get_filtered_questions(
        user_id, selected_topics, date_range, difficulty, None
    )
    
    with tabs[0]:
        display_questions_list(filtered_questions)
    
    with tabs[1]:
        incorrect_questions = [q for q in filtered_questions if q['qua'] != q['qra']]
        display_questions_list(incorrect_questions)
    
    with tabs[2]:
        topic_breakdown = create_topic_breakdown(filtered_questions)
        if topic_breakdown:
            fig3 = create_topic_chart(topic_breakdown)
            st.plotly_chart(fig3, use_container_width=True, key="topic_chart")
        else:
            st.info("No topic breakdown available.")

    # AI Learning Assistant
    st.subheader("AI Learning Assistant")
    user_query = st.text_input("Ask about your performance or get learning recommendations!")
    
    if st.button("Ask"):
        if user_query:
            context = {
                'analytics': analytics if analytics else [],
                'recent_questions': filtered_questions[-5:] if filtered_questions else [],
                'topic_breakdown': topic_breakdown if topic_breakdown else {}
            }
            response = ai_assistant.get_response(user_query, context)
            
            with st.chat_message("assistant"):
                st.write(response)

def create_performance_chart(analytics):
    if not analytics:
        return go.Figure()
    try:
        df = pd.DataFrame(analytics)
        if df.empty:
            return go.Figure()
            
        fig = go.Figure(data=[
            go.Bar(
                name='Correct',
                y=df['q_topic'],
                x=df['correct_answers'],
                orientation='h',
                marker_color='green'
            ),
            go.Bar(
                name='Incorrect',
                y=df['q_topic'],
                x=df['total_questions'] - df['correct_answers'],
                orientation='h',
                marker_color='red'
            )
        ])
        
        fig.update_layout(
            title='Performance by Topic',
            barmode='stack',
            xaxis_title='Number of Questions',
            yaxis_title='Topics',
            height=400
        )
        return fig
    except Exception as e:
        print(f"Error creating performance chart: {e}")
        return go.Figure()

def create_mastery_heatmap(analytics):
    """Creates a heatmap showing topic mastery levels"""
    if not analytics:
        return go.Figure()
    
    df = pd.DataFrame(analytics)
    df['mastery_pct'] = df['correct_answers'] / df['total_questions'] * 100
    
    fig = px.imshow(
        df.pivot_table(
            values='mastery_pct',
            columns='q_topic',
            aggfunc='mean'
        ),
        labels=dict(color="Mastery %"),
        color_continuous_scale="RdYlGn",
        aspect="auto"
    )
    
    fig.update_layout(
        title='Topic Mastery Heatmap',
        height=300
    )
    return fig

def get_filtered_questions(user_id, topics, date_range, difficulty, mastery_range):
    try:
        questions = db.get_user_questions(user_id)
        if not questions:
            return []
        
        filtered = [q for q in questions if (
            (not topics or q['q_topic'] in topics) and
            (difficulty == "All" or q['qdiff'] == difficulty) and
            (not mastery_range or mastery_range[0] <= float(q.get('topic_mastery', 0)) <= mastery_range[1]) and
            (not date_range or (
                datetime.strptime(str(q['created_at']), '%Y-%m-%d %H:%M:%S').date() >= date_range[0] and
                datetime.strptime(str(q['created_at']), '%Y-%m-%d %H:%M:%S').date() <= date_range[1]
            ))
        )]
        
        return filtered
    except Exception as e:
        print(f"Error filtering questions: {e}")
        return []

def create_topic_breakdown(questions):
    """Creates a breakdown of performance by topic"""
    breakdown = {}
    for q in questions:
        topic = q['q_topic']
        if topic not in breakdown:
            breakdown[topic] = {
                'total': 0,
                'correct': 0,
                'incorrect': 0,
                'mastery': 0.0
            }
        
        breakdown[topic]['total'] += 1
        if q.get('qua') == q.get('qra'):
            breakdown[topic]['correct'] += 1
        else:
            breakdown[topic]['incorrect'] += 1
        
        breakdown[topic]['mastery'] = (
            breakdown[topic]['correct'] / breakdown[topic]['total'] * 100
        )
    
    return breakdown

def create_topic_chart(breakdown):
    """Creates a radar chart showing topic mastery"""
    if not breakdown:
        return go.Figure()
    
    fig = go.Figure(data=go.Scatterpolar(
        r=[v['mastery'] for v in breakdown.values()],
        theta=list(breakdown.keys()),
        fill='toself',
        name='Topic Mastery'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title='Topic Mastery Overview',
        showlegend=False
    )
    return fig

def get_next_topic_suggestions(analytics):
    """Suggests next topics to study based on performance"""
    if not analytics:
        return []
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(analytics)
    df['mastery'] = df['correct_answers'] / df['total_questions'] * 100
    
    # Sort by mastery level and get bottom 3
    weak_topics = df.nsmallest(3, 'mastery')
    
    suggestions = []
    for _, topic in weak_topics.iterrows():
        suggestions.append({
            'topic': topic['q_topic'],
            'mastery': topic['mastery'],
            'suggestion': (
                "Needs immediate attention"
                if topic['mastery'] < 50
                else "Could use more practice"
            )
        })
    
    return suggestions

def display_questions_list(questions):
    """Displays a list of questions with details"""
    if not questions:
        st.info("No questions found matching the criteria.")
        return
    
    for idx, q in enumerate(questions, 1):
        with st.expander(f"Question {idx}: {q['q_title']}"):
            st.write(f"**Topic:** {q['q_topic']}")
            st.write(f"**Difficulty:** {q['qdiff']}")
            st.write(f"**Your Answer:** {q.get('qua', 'Not answered')}")
            st.write(f"**Correct Answer:** {q['qra']}")
            st.write(f"**Explanation:** {q['qex']}")
            
            # Show mastery progress
            if 'topic_mastery' in q:
                st.progress(float(q['topic_mastery']) / 100)
                st.write(f"Topic Mastery: {q['topic_mastery']:.1f}%")


def clear_session_state():
    keys_to_remove = ['generated_questions', 'user_answers']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

if st.session_state['user_id']:
    st.sidebar.title(f"Welcome, {st.session_state['user_name']}")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.success("Logged out successfully.")
        st.rerun()
    
    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate", ["Upload PDF", "Generate Questions", "Analyze Questions"])
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
    elif page == "Analyze Questions":
        analyze_questions_page()
# Close Database Connection on App Exit
def on_exit():
    if not db._is_closed:  # Check if the connection is already closed
        
        db.close()

import atexit
atexit.register(on_exit)