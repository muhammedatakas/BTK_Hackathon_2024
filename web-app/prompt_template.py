# PROMPT_TEMPLATE.PY

import os
import json
import google.generativeai as genai
from database import Database

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

# Initialize Database
db = Database()

# Class to generate questions
class QuestionGenerator:
    def __init__(self, api_key, db_instance):    
        self.api_key = api_key
        self.db = db_instance
        print("QuestionGenerator initialized.")
    
    def generate_questions_for_user(self, user_id):
        print(f"Generating questions for user_id: {user_id}")
        # Retrieve PDF data for the user
        pdf_data = self.db.get_user_pdf_data(user_id)
        if not pdf_data:
            print("No PDF data found for the user.")
            return

        # Iterate through each PDF entry for the user
        for data in pdf_data:
            pdf_name = data['pdf_name']
            pdf_category = data['pdf_category']
            pdf_summary = data['pdf_summary']
            print(f"Generating questions for PDF: {pdf_name}")

            # Generate question based on PDF summary
            question_data = self.generate_questions_from_summary(pdf_name, pdf_summary, pdf_category)

            # Validate the generated question
            if self.validate_question_data(question_data):
                # Store question data in the database
                self.db.insert_user_question(user_id, question_data)
                print(f"Question stored: {question_data['q_title']}")
            else:
                print("Generated question data is invalid.")

    def generate_questions_from_summary(self, pdf_name, pdf_summary, pdf_category, difficulty="Medium"):
        """
        Generate a multiple-choice question based on the PDF name, category, and summary.
        """
        prompt = self.create_prompt_template(pdf_name, pdf_summary, pdf_category, difficulty)
        print(f"Generated prompt: {prompt}")
        try:
            response = chat_session.send_message(prompt)
            print("Received response from Gemini LLM.")
        except Exception as e:
            print(f"Error sending message to Gemini LLM: {e}")
            return None

        if response is None or not hasattr(response, 'text'):
            print("Invalid response received from Gemini LLM.")
            return None

        question_data = self.parse_llm_response(response)
        if question_data:
            question_data['difficulty'] = difficulty  # Add difficulty to question data
            print(f"Parsed question data: {question_data}")
        return question_data

    def parse_llm_response(self, response):
        """
        Parse the response from the Gemini LLM into a structured dictionary format.
        """
        try:
            response_text = response.text.strip().strip("```json").strip("```").strip()
            print(f"Response text: {response_text}")
            question_data = json.loads(response_text)
            print("JSON parsing successful.")
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
        1. A clear title (q_title) in question format.
        2. The topic (q_topic) based on the category.
        3. Four distinct and plausible answer options (opt_a, opt_b, opt_c, opt_d).
        4. The correct answer and a detailed explanation of why it's correct.

        Please format the question as:
        {{
            "q_title": "<insert question title>",
            "q_topic": "<insert topic>",
            "opt_a": "<insert option A>",
            "opt_b": "<insert option B>",
            "opt_c": "<insert option C>",
            "opt_d": "<insert option D>",
            "answer": "<insert correct answer>",
            "explanation": "<insert explanation>"
        }}
        """
        print(f"Created prompt for PDF '{pdf_name}'.")
        return prompt

    def validate_question_data(self, question_data):
        """
        Validate that the generated question data contains all necessary fields.
        """
        required_fields = ['q_title', 'q_topic', 'opt_a', 'opt_b', 'opt_c', 'opt_d', 'answer', 'explanation']
        if question_data is None:
            print("No question data to validate.")
            return False

        for field in required_fields:
            if field not in question_data or not question_data[field]:
                print(f"Missing or empty field: {field}")
                return False

        print("Question data validation passed.")
        return True

# Example usage
if __name__ == "__main__":
    # Specify the user ID you want to generate questions for
    user_id = 1  # Replace with the actual user ID
    
    # Generate questions for the user based on their PDF data
    q_gen = QuestionGenerator(api_key=api_key, db_instance=db)
    q_gen.generate_questions_for_user(user_id)
    
    # Close the database connection
    db.close()