# DATABASE.PY

import mysql.connector
from mysql.connector import Error

class Database: 
    def __init__(self) -> None: 
        try:
            # Environment variable ile bağlantı için (Yorum satırında)
            # self.connection = mysql.connector.connect(
            # host=os.environ.get('DB_HOST'),
            # user=os.environ.get('DB_USER'),
            # password=os.environ.get('DB_PASS'),
            # database=os.environ.get('DB_NAME')
            # )

            # Sabit bağlantı için (lokal bağlantı)
            self.connection = mysql.connector.connect(
                host="localhost",  
                user="root",
                password="ShmAkckl@1504.",
                database="mydb"
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("Database connection established.")
        except mysql.connector.Error as err:
            print(f"Error during connection: {err}")
    
    def get_user_by_email(self, email):
        try:
            print(f"Fetching user by email: {email}")
            self.cursor.execute('SELECT * FROM user WHERE user_email = %s', (email,))
            result = self.cursor.fetchone()
            print(f"get_user_by_email result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_by_email: {err}")
    
    def insert_user(self, user_id, name, surname, email, password) -> None:
        try:
            print(f"Inserting user: {user_id}, {name}, {surname}, {email}")
            self.cursor.execute('INSERT INTO user (user_id, user_name, user_surname, user_email, user_password) VALUES (%s, %s, %s, %s, %s)', 
                                (user_id, name, surname, email, password))
            self.connection.commit()
            print("User inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error in insert_user: {err}")
        
    def get_user_categories(self, user_id):
        try:
            print(f"Fetching categories for user_id: {user_id}")
            self.cursor.execute('SELECT DISTINCT pdf_category FROM user_data WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            print(f"get_user_categories result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_categories: {err}")
    
    def insert_summary(self, user_id, pdf_name, pdf_category, pdf_summary):
        try:
            print(f"Inserting summary for user_id: {user_id}, PDF: {pdf_name}")
            self.cursor.execute("""INSERT INTO user_data (user_id, pdf_name, pdf_category, pdf_summary) 
                                   VALUES (%s, %s, %s, %s)""", 
                                   (user_id, pdf_name, pdf_category, pdf_summary))
            self.connection.commit()
            print("Summary inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error in insert_summary: {err}")
        
    def get_summaries_by_category(self, user_id, category):
        try:
            print(f"Fetching summaries for user_id: {user_id}, category: {category}")
            self.cursor.execute("""
            SELECT pdf_name, pdf_category, pdf_summary 
            FROM user_data WHERE user_id = %s and pdf_category = %s
            """, (user_id, category)) 
            result = self.cursor.fetchall()
            print(f"get_summaries_by_category result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_summaries_by_category: {err}")
    
    def get_user_pdf_data(self, user_id):
        try:
            print(f"Fetching PDF data for user_id: {user_id}")
            self.cursor.execute("""
            SELECT pdf_name, pdf_category, pdf_summary 
            FROM user_data WHERE user_id = %s 
            """, (user_id,))  # Ensure it's a tuple
            result = self.cursor.fetchall()
            print(f"get_user_pdf_data result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_pdf_data: {err}")
            
    def get_user_questions(self, user_id):
        try:
            print(f"Fetching questions for user_id: {user_id}")
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s', (user_id,))
            result = self.cursor.fetchall()
            print(f"get_user_questions result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_questions: {err}")
            
    
    def get_user_questions_by_category(self, user_id, q_topic):
        try:
            print(f"Fetching questions for user_id: {user_id}, topic: {q_topic}")
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and q_topic = %s', (user_id, q_topic))
            result = self.cursor.fetchall()
            print(f"get_user_questions_by_category result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_questions_by_category: {err}")
    
    def insert_user_question(self, user_id, question: dict):
        try:
            print(f"Inserting question for user_id: {user_id}, question: {question['q_title']}")
            self.cursor.execute("""
            INSERT INTO user_question(user_id, q_topic, q_title, qA, qB, qC, qD, qra, qua, qex, qdiff)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, question["q_topic"], question["q_title"],
                  question["opt_a"], question["opt_b"], question["opt_c"], question["opt_d"], 
                  question["answer"], question.get("qua",None), question["explanation"], question["difficulty"])) 
            self.connection.commit()
            print("Question inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error in insert_user_question: {err}")
    
    def get_user_incorrect_questions(self, user_id): 
        try:
            print(f"Fetching incorrect questions for user_id: {user_id}")
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and qua <> qra', (user_id,))
            result = self.cursor.fetchall()
            print(f"get_user_incorrect_questions result: {result}")
            return result
        except mysql.connector.Error as err:
            print(f"Error in get_user_incorrect_questions: {err}")
        
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Database connection closed.")