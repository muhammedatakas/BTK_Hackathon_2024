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
import random
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
    if 'generated_questions' in st.session_state and not st.session_state.get('show_generation', False):
        display_questions()
    else:
        # Clear any existing state
        if 'show_generation' in st.session_state:
            del st.session_state['show_generation']
            
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
        quantity = st.slider("Number of Questions to Generate", min_value=1, max_value=10, value=5)

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
    # Add Generate New Questions button at the top
    
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
                
                clear_session_state()
                # Add Generate Again button
                if st.button("Generate New Questions", key="generate_new"):
                    
                    # Force page refresh
                    st.rerun()
                        
            else:
                st.error("Failed to submit any questions. Please try again.")

        except Exception as e:
            st.error(f"Error submitting answers: {str(e)}")
            print(f"Error details: {e}")

# Update practice_mode_page in APP.PY

def practice_mode_page():
    st.header("Practice Mode")
    user_id = st.session_state['user_id']
    
    # Get user's analytics and incorrect questions
    analytics = db.get_user_question_analytics(user_id)
    incorrect_questions = db.get_user_incorrect_questions(user_id)
    
    if not analytics or not incorrect_questions:
        st.info("Complete some questions first to enable practice mode.")
        return
    
    # Convert to DataFrame and ensure proper types
    df = pd.DataFrame(analytics)
    df['mastery'] = (df['correct_answers'] / df['total_questions'] * 100).astype(float)
    df['q_topic'] = df['q_topic'].astype(str)
    
    # Display topic selection based on mastery levels
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Topic Mastery Overview")
        for _, topic in df.iterrows():
            topic_name = topic['q_topic']
            mastery = float(topic['mastery'])
            st.write(f"**{topic_name}**")
            st.progress(min(max(mastery/100, 0), 1))
            st.write(f"Current Mastery: {mastery:.1f}%")
        
        # Show improvement potential
        st.subheader("Areas for Improvement")
        incorrect_by_topic = {}
        for q in incorrect_questions:
            topic = q['q_topic']
            if topic not in incorrect_by_topic:
                incorrect_by_topic[topic] = 0
            incorrect_by_topic[topic] += 1
        
        for topic, count in incorrect_by_topic.items():
            st.warning(f"📚 {topic}: {count} questions to review")
    
    with col2:
        st.subheader("Practice Options")
        
        # Topic selection from incorrect answers
        topics_with_errors = list(incorrect_by_topic.keys())
        if topics_with_errors:
            selected_topic = st.selectbox(
                "Select Topic to Practice",
                options=topics_with_errors,
                index=0
            )
            
            practice_type = st.radio(
                "Practice Type",
                ["Review Wrong Answers", "Generate New Questions"]
            )
            
            time_limit = st.slider(
                "Time Limit (minutes)",
                min_value=1,
                max_value=30,
                value=5
            )
            
            if practice_type == "Review Wrong Answers":
                num_questions = st.slider(
                    "Number of Questions",
                    min_value=1,
                    max_value=len([q for q in incorrect_questions if q['q_topic'] == selected_topic]),
                    value=min(5, len([q for q in incorrect_questions if q['q_topic'] == selected_topic]))
                )
            else:
                num_questions = st.slider(
                    "Number of Questions",
                    min_value=1,
                    max_value=10,
                    value=5
                )
            
            difficulty = st.selectbox(
                "Difficulty",
                options=["Easy", "Medium", "Hard"]
            )
            
            if st.button("Start Practice Session"):
                if practice_type == "Review Wrong Answers":
                    # Get wrong answers for selected topic
                    topic_wrong_questions = [q for q in incorrect_questions if q['q_topic'] == selected_topic]
                    selected_questions = random.sample(topic_wrong_questions, min(num_questions, len(topic_wrong_questions)))
                    
                    # Store questions in session state
                    st.session_state['practice_questions'] = selected_questions
                    st.session_state['practice_start_time'] = datetime.now()
                    st.session_state['practice_time_limit'] = time_limit
                    st.session_state['practice_type'] = 'review'
                else:
                    # Generate new questions
                    topic_pdfs = db.get_summaries_by_category(user_id, selected_topic)
                    if not topic_pdfs:
                        st.error("No PDFs found for this topic. Please upload relevant PDFs first.")
                        return
                    
                    with st.spinner("Generating practice questions..."):
                        practice_questions = []
                        for pdf in topic_pdfs:
                            question_data = q_gen.generate_questions_from_summary(
                                pdf['pdf_name'],
                                pdf['pdf_summary'],
                                selected_topic,
                                difficulty
                            )
                            if question_data:
                                practice_questions.append(question_data)
                            if len(practice_questions) >= num_questions:
                                break
                        
                        if practice_questions:
                            st.session_state['practice_questions'] = practice_questions
                            st.session_state['practice_start_time'] = datetime.now()
                            st.session_state['practice_time_limit'] = time_limit
                            st.session_state['practice_type'] = 'new'
                
                st.rerun()
        else:
            st.info("No incorrect answers found. Try generating new questions!")

    # Show practice session if active
    if 'practice_questions' in st.session_state:
        display_timed_practice_session()

def display_timed_practice_session():
    st.header("Timed Practice Session")
    
    # Calculate remaining time
    elapsed_time = datetime.now() - st.session_state['practice_start_time']
    remaining_seconds = max(0, st.session_state['practice_time_limit'] * 60 - elapsed_time.total_seconds())
    
    # Display timer
    col1, col2 = st.columns([3, 1])
    with col2:
        st.write("Time Remaining:")
        st.write(f"{int(remaining_seconds // 60)}:{int(remaining_seconds % 60):02d}")
    
    # Check if time's up
    if remaining_seconds <= 0:
        st.warning("Time's up! Please submit your answers.")
    
    # Display questions
    questions = st.session_state['practice_questions']
    if 'practice_answers' not in st.session_state:
        st.session_state['practice_answers'] = {}
    
    for idx, question in enumerate(questions):
        st.subheader(f"Question {idx + 1}")
        if st.session_state['practice_type'] == 'review':
            st.info(f"Previous answer: {question['qua']} (Incorrect)")
        
        st.write(question['q_title'])
        
        options = {
            'A': question.get('opt_a', question.get('qA')),
            'B': question.get('opt_b', question.get('qB')),
            'C': question.get('opt_c', question.get('qC')),
            'D': question.get('opt_d', question.get('qD'))
        }
        
        answer = st.radio(
            "Select your answer:",
            options=['A', 'B', 'C', 'D'],
            format_func=lambda x: f"{x}: {options[x]}",
            key=f"practice_{idx}"
        )
        
        st.session_state['practice_answers'][idx] = answer
    
    # Submit button
    if st.button("Submit Practice Session"):
        submit_practice_session(questions)

def submit_practice_session(questions):
    score = 0
    user_id = st.session_state['user_id']
    
    for idx, question in enumerate(questions):
        user_answer = st.session_state['practice_answers'].get(idx)
        correct_answer = question.get('answer', question.get('qra'))
        
        if user_answer == correct_answer:
            score += 1
        
        # Update question in database
        if st.session_state['practice_type'] == 'review':
            db.update_question_attempt(question['question_id'], user_answer, user_answer == correct_answer)
        else:
            db.insert_user_question(user_id, {
                'q_topic': question['q_topic'],
                'q_title': question['q_title'],
                'opt_a': question['opt_a'],
                'opt_b': question['opt_b'],
                'opt_c': question['opt_c'],
                'opt_d': question['opt_d'],
                'qra': correct_answer,
                'qua': user_answer,
                'qex': question['explanation'],
                'qdiff': question['difficulty']
            })
    
    # Show results
    st.success(f"Practice Session Complete!\nScore: {score}/{len(questions)} ({(score/len(questions))*100:.1f}%)")
    
    # Show explanations
    for idx, question in enumerate(questions):
        with st.expander(f"Question {idx + 1} Explanation"):
            user_answer = st.session_state['practice_answers'].get(idx)
            correct_answer = question.get('answer', question.get('qra'))
            st.write(f"Your answer: {user_answer}")
            st.write(f"Correct answer: {correct_answer}")
            st.write(f"Explanation: {question['explanation']}")
    
    # Clear practice session
    if st.button("Start New Practice Session"):
        for key in ['practice_questions', 'practice_answers', 'practice_start_time', 'practice_time_limit', 'practice_type']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
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
    st.header("Learning Recommendations")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Topics to Focus On")
        recommendations = db.get_topic_recommendations(user_id)
        if recommendations:
            for rec in recommendations:
                with st.expander(f"📚 {rec['q_topic']}"):
                    # Ensure mastery is a valid float between 0 and 100
                    mastery = float(rec['avg_mastery']) if rec['avg_mastery'] is not None else 0.0
                    mastery = min(max(mastery, 0.0), 100.0)
                    
                    # Display progress bar
                    st.progress(mastery/100)
                    st.write(f"Current Mastery: {mastery:.1f}%")
                    
                    # Show recommendations based on mastery level
                    if mastery < 50:
                        st.error("⚠️ Needs immediate attention")
                        st.write("Recommendation: Focus on basic concepts and review material")
                    elif mastery < 75:
                        st.warning("📝 Could use more practice")
                        st.write("Recommendation: Practice regularly to improve understanding")
                    else:
                        st.success("✅ Good progress")
                        st.write("Recommendation: Challenge yourself with harder questions")
    
    with col2:
        st.subheader("Study Plan")
        if recommendations:
            st.write("Suggested study order:")
            for idx, rec in enumerate(recommendations, 1):
                topic = rec['q_topic']
                mastery = float(rec['avg_mastery']) if rec['avg_mastery'] is not None else 0.0
                mastery = min(max(mastery, 0.0), 100.0)
                
                if mastery < 50:
                    priority = "High Priority"
                    emoji = "🔴"
                elif mastery < 75:
                    priority = "Medium Priority"
                    emoji = "🟡"
                else:
                    priority = "Low Priority"
                    emoji = "🟢"
                
                st.write(f"{idx}. {emoji} **{topic}** ({priority})")
                st.write(f"   Target: Improve mastery to {min(mastery + 20, 100):.1f}%")
                
                # Add practice button for each topic
                if st.button(f"Practice {topic}", key=f"practice_{topic}"):
                    st.session_state['practice_topic'] = topic
                    st.session_state['show_practice'] = True
                    st.rerun()
                
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
            st.write(f"A: {q['qA']}")
            st.write(f"B: {q['qB']}")
            st.write(f"C: {q['qC']}")
            st.write(f"D: {q['qD']}")
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
    page = st.sidebar.radio("Navigate", ["Upload PDF", "Generate Questions","Practice Mode", "Analyze Questions"])
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
    elif page == "Practice Mode":
        practice_mode_page()
    elif page == "Analyze Questions":
        analyze_questions_page()
# Close Database Connection on App Exit
def on_exit():
    if not db._is_closed:  # Check if the connection is already closed
        
        db.close()

import atexit
atexit.register(on_exit)