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


# Initialize Database
db = Database()

# Class to generate questions
class QuestionGenerator:
    def __init__(self, api_key, db_instance):    
        self.api_key = api_key
        self.db = db_instance
        self.chat_session = model.start_chat(history=[])
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
            response = self.chat_session.send_message(prompt)
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

    def create_prompt_template(self, pdf_name, pdf_summary, pdf_category, difficulty="Medium"):
        prompt = f"""
        You are an educational assistant. Based on the following document information, create a {difficulty} multiple-choice question.

        PDF Name: {pdf_name}
        Category: {pdf_category}
        Summary: {pdf_summary}

        Generate a single multiple-choice question in this exact JSON format:
        {{
            "q_title": "The actual question text here?",
            "q_topic": "{pdf_category}",
            "opt_a": "First option text",
            "opt_b": "Second option text",
            "opt_c": "Third option text",
            "opt_d": "Fourth option text",
            "answer": "A",
            "explanation": "Detailed explanation why the answer is correct",
            "difficulty": "{difficulty}"
        }}

        The answer field MUST be one of: "A", "B", "C", or "D" (uppercase only).
        """
        return prompt

    def parse_llm_response(self, response):
        try:
            # Clean up the response text
            response_text = response.text.strip()
            # Remove any markdown code block markers
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse the JSON
            question_data = json.loads(response_text)
            
            # Validate the answer format
            if question_data['answer'] not in ['A', 'B', 'C', 'D']:
                raise ValueError("Invalid answer format")
                
            return question_data
        except Exception as e:
            print(f"Error parsing response: {e}")
            print("Raw response:", response.text)
            return None

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

class AIAssistant:
    def __init__(self, api_key):
        self.api_key = api_key
        self.chat_session = model.start_chat(history=[])

    def get_response(self, query, context):
        """Generate contextual response based on user analytics"""
        prompt = f"""
        Context:
        - User's analytics: {context['analytics']}
        - Recent questions: {context['recent_questions']}
        - Topic breakdown: {context['topic_breakdown']}
        
        User Query: {query}
        
        Please provide a helpful response that:
        1. Addresses the user's question
        2. References their performance data
        3. Gives specific recommendations
        4. Maintains an encouraging tone
        """
        
        try:
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble generating a response right now."

# Example usage
if __name__ == "__main__":
    # Specify the user ID you want to generate questions for
    user_id = 1  # Replace with the actual user ID
    
    # Generate questions for the user based on their PDF data
    q_gen = QuestionGenerator(api_key=api_key, db_instance=db)
    q_gen.generate_questions_for_user(user_id)
    
    # Close the database connection
    db.close()