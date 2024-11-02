# DATABASE.PY

import mysql.connector
from mysql.connector import Error

class Database:
    
    _instance = None
    _is_closed = False  # Add this flag

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def close(self):
        if not self._is_closed and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            self._is_closed = True  # Set the flag to True
            print("Database connection closed.")
    def _initialize(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="147456Ata2073",
                database="mydb"
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database connection established.")
        except mysql.connector.Error as err:
            print(f"Error during connection: {err}")

    def get_user_by_email(self, email):
        try:
           
            self.cursor.execute('SELECT * FROM user WHERE user_email = %s', (email,))
            result = self.cursor.fetchone()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_by_email: {err}")

    def insert_user(self, user_id, name, surname, email, password) -> None:
        try:
           
            self.cursor.execute('INSERT INTO user (user_id, user_name, user_surname, user_email, user_password) VALUES (%s, %s, %s, %s, %s)', 
                                (user_id, name, surname, email, password))
            self.connection.commit()
            print("User inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error in insert_user: {err}")

    def get_user_categories(self, user_id):
        try:
            
            self.cursor.execute('SELECT DISTINCT pdf_category FROM user_data WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_categories: {err}")

    def insert_summary(self, user_id, pdf_name, pdf_category, pdf_summary):
        try:
            
            self.cursor.execute("""INSERT INTO user_data (user_id, pdf_name, pdf_category, pdf_summary) 
                                   VALUES (%s, %s, %s, %s)""", 
                                   (user_id, pdf_name, pdf_category, pdf_summary))
            self.connection.commit()
            print("Summary inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error in insert_summary: {err}")

    def get_summaries_by_category(self, user_id, category):
        try:
            
            self.cursor.execute("""
            SELECT pdf_name, pdf_category, pdf_summary 
            FROM user_data WHERE user_id = %s and pdf_category = %s
            """, (user_id, category)) 
            result = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_summaries_by_category: {err}")

    def get_user_pdf_data(self, user_id):
        try:
            
            self.cursor.execute("""
            SELECT pdf_name, pdf_category, pdf_summary 
            FROM user_data WHERE user_id = %s 
            """, (user_id,))  # Ensure it's a tuple
            result = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_pdf_data: {err}")

    def get_user_questions(self, user_id):
        try:
            
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_questions: {err}")

    def get_user_questions_by_category(self, user_id, q_topic):
        try:
            print(f"Fetching questions for user_id: {user_id}, topic: {q_topic}")
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and q_topic = %s', (user_id, q_topic))
            result = self.cursor.fetchall()
            
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_questions_by_category: {err}")

    # In DATABASE.PY - Fix insert_user_question method
    def insert_user_question(self, user_id, question):
        try:
            print(f"Inserting question for user {user_id}: {question}")  # Debug log
            self.cursor.execute("""
                INSERT INTO user_question
                (user_id, q_topic, q_title, qA, qB, qC, qD, qra, qua, qex, qdiff)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                question["q_topic"],
                question["q_title"],
                question["opt_a"],
                question["opt_b"],
                question["opt_c"],
                question["opt_d"],
                question["qra"],
                question["qua"],
                question["qex"],
                question["qdiff"]
            ))
            self.connection.commit()
            print("Question inserted successfully")  # Debug log
            return True
        except mysql.connector.Error as err:
            print(f"Error in insert_user_question: {err}")
            return False

    # In DATABASE.PY - Fix duplicate get_user_incorrect_questions method
# Remove the duplicate method and keep only one implementation:

    def get_user_incorrect_questions(self, user_id): 
        try:
            print(f"Fetching incorrect questions for user_id: {user_id}")
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and qua <> qra', (user_id,))
            result = self.cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_incorrect_questions: {err}")
            return None

    def update_topic_mastery(self, user_id, topic, correct_answer):
        """Update topic mastery based on user performance"""
        try:
            self.cursor.execute("""
                UPDATE user_question 
                SET topic_mastery = (
                    SELECT (COUNT(CASE WHEN qua = qra THEN 1 END) * 100.0 / COUNT(*))
                    FROM user_question q2
                    WHERE q2.user_id = %s AND q2.q_topic = %s
                )
                WHERE user_id = %s AND q_topic = %s
            """, (user_id, topic, user_id, topic))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error updating topic mastery: {err}")

    def get_topic_recommendations(self, user_id):
        """Get personalized topic recommendations based on performance"""
        try:
            self.cursor.execute("""
                SELECT q_topic, 
                    AVG(topic_mastery) as avg_mastery,
                    COUNT(*) as question_count
                FROM user_question
                WHERE user_id = %s
                GROUP BY q_topic
                ORDER BY avg_mastery ASC
                LIMIT 3
            """, (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting topic recommendations: {err}")

    def add_question_tracking_columns(self):
        try:
            self.cursor.execute("""
                ALTER TABLE user_question 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ADD COLUMN topic_mastery FLOAT DEFAULT 0.0,
                ADD COLUMN attempt_count INT DEFAULT 1
            """)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error adding tracking columns: {err}")

    # Update get_user_question_analytics in DATABASE.PY
    def delete_pdf(self, user_id, pdf_name):
        try:
            self.cursor.execute("""
                DELETE FROM user_data 
                WHERE user_id = %s AND pdf_name = %s
            """, (user_id, pdf_name))
            self.connection.commit()
            print(f"PDF '{pdf_name}' deleted successfully.")
        except mysql.connector.Error as err:
            print(f"Error deleting PDF: {err}")
            raise err

    def delete_category(self, user_id, category):
        try:
            # Delete all PDFs in category
            self.cursor.execute("""
                DELETE FROM user_data 
                WHERE user_id = %s AND pdf_category = %s
            """, (user_id, category))
            self.connection.commit()
            print(f"Category '{category}' deleted successfully.")
        except mysql.connector.Error as err:
            print(f"Error deleting category: {err}")
            raise err
    def get_user_question_analytics(self, user_id):
        try:
            self.cursor.execute("""
                SELECT 
                    q_topic,
                    COUNT(*) as total_questions,
                    SUM(CASE WHEN qua = qra THEN 1 ELSE 0 END) as correct_answers,
                    AVG(CASE WHEN qua = qra THEN 1 ELSE 0 END) * 100 as topic_mastery
                FROM user_question 
                WHERE user_id = %s 
                GROUP BY q_topic
            """, (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error getting analytics: {err}")
            return []  # Return empty list instead of None
    def update_question_attempt(self, question_id, new_answer, is_correct):
        try:
            self.cursor.execute("""
                UPDATE user_question 
                SET qua = %s, 
                    attempt_count = attempt_count + 1,
                    topic_mastery = CASE 
                        WHEN %s THEN ((topic_mastery * attempt_count) + 100) / (attempt_count + 1)
                        ELSE (topic_mastery * attempt_count) / (attempt_count + 1)
                    END
                WHERE question_id = %s
            """, (new_answer, is_correct, question_id))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error updating question attempt: {err}")
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")