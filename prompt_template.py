import os
import google.generativeai as genai
import json

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

class Question_Generator:
    def __init__(self, api_key):
        self.api_key = api_key

    # Function to generate a question based on PDF summary
    def generate_questions_from_summary(self, pdf_name, pdf_summary):
        """
        Generate a multiple-choice question based on the PDF name and summary using the Gemini LLM.
        """
        prompt = self.create_prompt_template(pdf_name, pdf_summary)

        # Call Gemini LLM with the prompt
        try:
            response = chat_session.send_message(prompt)
        except Exception as e:
            print(f"Error sending message to Gemini LLM: {e}")
            return None

        # Ensure the response is valid
        if response is None or not hasattr(response, 'text'):
            print("Invalid response received from Gemini LLM.")
            return None

        # Parse the response into structured data
        question_data = self.parse_llm_response(response)
        return question_data

    # Parse the response from the LLM
    def parse_llm_response(self, response):
        """
        Parse the response from the Gemini LLM into a structured dictionary format.
        """
        try:
            # Remove backticks or other extraneous characters and parse as JSON
            response_text = response.text.strip().strip("```json").strip("```").strip()
            question_data = json.loads(response_text)
            return question_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print("Response content:", response.text)
            return None

    # Template to create the prompt for the LLM
    def create_prompt_template(pdf_name, pdf_summary, difficulty="Medium"):
        prompt = f"""
        You are an educational assistant. Based on the following summary of a document, create a {difficulty} multiple-choice question.

        PDF Name: {pdf_name}

        Summary: {pdf_summary}

        The question should include:
        1. A clear title (q-title) in question format.
        2. The topic (q-topic).
        3. Four distinct and plausible answer options (opt_a, opt_b, opt_c, opt_d).
        4. The correct answer and a detailed explanation of why it's correct.

        Difficulty level: {difficulty}

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


    # Validate the question data structure
    def validate_question_data(self, question_data):
        """
        Validate that the generated question data contains all necessary fields.
        """
        required_fields = ['q-title', 'q-topic', 'opt_a', 'opt_b', 'opt_c', 'opt_d', 'answer', 'explanation']

        # Check if question_data is None
        if question_data is None:
            print("No question data to validate.")
            return False

        # Check all required fields
        for field in required_fields:
            if field not in question_data or not question_data[field]:
                print(f"Missing or empty field: {field}")
                return False

        return True

    # Main function to generate and validate the question
    def generate_and_validate_question(self, pdf_name, pdf_summary):
        """
        Generate a question and validate its structure.
        """
        question_data = self.generate_questions_from_summary(pdf_name, pdf_summary)
        if self.validate_question_data(question_data):
            return question_data
        else:
            print("Invalid question data generated.")
            return None


# Example usage
if __name__ == "__main__":
    q = Question_Generator(api_key=api_key)
    # Example PDF summary
    example_pdf_name = "Artificial_Intelligence_and_Society"
    example_pdf_summary = "Artificial Intelligence (AI) is transforming industries across the globe. From healthcare to finance, AI systems are being used to automate tasks, analyze data, and make decisions faster and more accurately than ever before. This shift has sparked discussions on the role of AI in society, including concerns about privacy, job displacement, and ethical implications of AI-driven decisions. Despite these challenges, AI continues to push technological boundaries, and its applications are expanding at a rapid pace."


    # Generate and validate the question
    question_data = q.generate_and_validate_question(example_pdf_name, example_pdf_summary)
    if question_data:
        print("Generated Question:", question_data)