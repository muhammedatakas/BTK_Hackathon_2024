import streamlit as st

def quiz_app(questions):
    st.title("Quiz App")
    
    # Dictionary to hold user's answers
    user_answers = {}

    # Loop through each question
    for i, question in enumerate(questions):
        st.header(f"Question {i + 1}")
        st.write(question['question'])
        
        # Radio buttons for selecting an answer
        options = question['options']
        user_answers[i] = st.radio(f"Select an answer for question {i + 1}:", options, key=i)

    # Submit button
    if st.button("Submit Quiz"):
        score = 0
        st.write("### Quiz Results:")
        
        # Check each answer
        for i, question in enumerate(questions):
            if user_answers[i] == question['answer']:
                st.write(f"Question {i + 1}: **Correct** 🎉")
                score += 1
            else:
                st.write(f"Question {i + 1}: **Wrong** ❌ (Correct answer: {question['answer']})")
        
        # Display total score
        st.write(f"Your total score is {score} out of {len(questions)}")
        
        if score == len(questions):
            st.balloons()

# Example usage
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "answer": "Paris"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars"
    }
]

if __name__ == "__main__":
    quiz_app(questions)
