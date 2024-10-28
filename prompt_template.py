import os
import google.generativeai as genai
import json
import mysql.connector

# Load API Key
api_key = os.environ.get('API_KEY')
if api_key:
    print("API Key retrieved successfully.")
else:
    print("API Key not found. Please set the environment variable.")
    exit()

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
)

chat_session = model.start_chat(history=[])

# Connect to MySQL Database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",        # Host
            port=3306,               # Port
            user="root",             # Replace with your DB username
            password="147456Ata2073",# Replace with your new DB password
            database="mydb"          # Database name
        )
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# Retrieve PDF data for a specific user
def get_user_pdf_data(connection, user_id):
    """
    Retrieve PDF data (name, category, summary) for a specific user.
    """
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT pid, pdf_name, pdf_category, pdf_summary
            FROM user_data
            WHERE user_id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchall()
        cursor.close()
        return result
    except mysql.connector.Error as e:
        print(f"Error retrieving PDF data: {e}")
        return None

# Store generated question in the user_question table for a specific user
def store_user_question(connection, question_data, user_id):
    """
    Store generated question data in the user_question table.
    """
    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO user_question (user_id, q_topic, q_title, qA, qB, qC, qD, qra, qua, qex, qdiff)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id,
            question_data['q-topic'],
            question_data['q-title'],
            question_data['opt_a'],
            question_data['opt_b'],
            question_data['opt_c'],
            question_data['opt_d'],
            question_data['answer'],
            question_data['answer'],  # Assuming 'qua' is the same as 'answer'
            question_data['explanation'],
            question_data.get('difficulty', "Medium")  # Default difficulty level if not specified
        )
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        print("Question data stored successfully.")
    except mysql.connector.Error as e:
        print(f"Error storing question data: {e}")

# Class to generate questions
class QuestionGenerator:
    def __init__(self, api_key, db_connection):    
        self.api_key = api_key
        self.db_connection = db_connection

    def generate_questions_for_user(self, user_id):
        # Retrieve PDF data for the user
        pdf_data = get_user_pdf_data(self.db_connection, user_id)
        if not pdf_data:
            print("No PDF data found for the user.")
            return

        # Iterate through each PDF entry for the user
        for data in pdf_data:
            pdf_name = data['pdf_name']
            pdf_category = data['pdf_category']
            pdf_summary = data['pdf_summary']

            # Generate question based on PDF summary
            question_data = self.generate_questions_from_summary(pdf_name, pdf_summary, pdf_category)

            # Validate the generated question
            if self.validate_question_data(question_data):
                # Store question data in the database
                store_user_question(self.db_connection, question_data, user_id)
            else:
                print("Generated question data is invalid.")

    def generate_questions_from_summary(self, pdf_name, pdf_summary, pdf_category, difficulty="Medium"):
        """
        Generate a multiple-choice question based on the PDF name, category, and summary.
        """
        prompt = self.create_prompt_template(pdf_name, pdf_summary, pdf_category, difficulty)
        try:
            response = chat_session.send_message(prompt)
        except Exception as e:
            print(f"Error sending message to Gemini LLM: {e}")
            return None

        if response is None or not hasattr(response, 'text'):
            print("Invalid response received from Gemini LLM.")
            return None

        question_data = self.parse_llm_response(response)
        question_data['difficulty'] = difficulty  # Add difficulty to question data
        return question_data

    def parse_llm_response(self, response):
        """
        Parse the response from the Gemini LLM into a structured dictionary format.
        """
        try:
            response_text = response.text.strip().strip("```json").strip("```").strip()
            question_data = json.loads(response_text)
            return question_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print("Response content:", response.text)
            return None

    def create_prompt_template(self, pdf_name, pdf_summary, pdf_category, difficulty="Medium"):
        prompt = f"""
        You are an educational assistant. Based on the following document information, create a {difficulty} multiple-choice question.

        PDF Name: {pdf_name}
        Category: {pdf_category}
        Summary: {pdf_summary}

        The question should include:
        1. A clear title (q-title) in question format.
        2. The topic (q-topic) based on the category.
        3. Four distinct and plausible answer options (opt_a, opt_b, opt_c, opt_d).
        4. The correct answer and a detailed explanation of why it's correct.

        Please format the question as:
        {{
            "q-title": "<insert question title>",
            "q-topic": "<insert topic>",
            "opt_a": "<insert option A>",
            "opt_b": "<insert option B>",
            "opt_c": "<insert option C>",
            "opt_d": "<insert option D>",
            "answer": "<insert correct answer>",
            "explanation": "<insert explanation>"
        }}
        """
        return prompt

    def validate_question_data(self, question_data):
        """
        Validate that the generated question data contains all necessary fields.
        """
        required_fields = ['q-title', 'q-topic', 'opt_a', 'opt_b', 'opt_c', 'opt_d', 'answer', 'explanation']
        if question_data is None:
            print("No question data to validate.")
            return False

        for field in required_fields:
            if field not in question_data or not question_data[field]:
                print(f"Missing or empty field: {field}")
                return False

        return True

# Example usage
if __name__ == "__main__":
    # Connect to the database
    db_connection = connect_to_database()
    
    # Initialize Question Generator
    q_gen = QuestionGenerator(api_key=api_key, db_connection=db_connection)

    # Specify the user ID you want to generate questions for
    user_id = 1  # Replace with the actual user ID

    # Generate questions for the user based on their PDF data
    q_gen.generate_questions_for_user(user_id)

    # Close the database connection
    if db_connection.is_connected():
        db_connection.close()
