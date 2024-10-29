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
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def get_user_by_email(self, email):
        try:
            self.cursor.execute('SELECT * FROM user WHERE user_email = %s', (email,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def insert_user(self, user_id, name, surname, email, password) -> None:
        try:
            self.cursor.execute('INSERT INTO user (user_id, user_name, user_surname, user_email, user_password) VALUES (%s, %s, %s, %s, %s)', 
                                (user_id, name, surname, email, password))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    def get_user_categories(self, user_id):
        try:
            self.cursor.execute('SELECT DISTINCT pdf_category FROM user_data WHERE user_id = %s', (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def insert_summary(self, user_id, pdf_name, pdf_category, pdf_summary):
        try:
            self.cursor.execute("""INSERT INTO user_data (user_id, pdf_name, pdf_category, pdf_summary) 
                                   VALUES (%s, %s, %s, %s)""", 
                                   (user_id, pdf_name, pdf_category, pdf_summary))
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    def get_summaries_by_category(self, user_id, category):
        try:
            self.cursor.execute("""
            SELECT pdf_name, pdf_category, pdf_summary 
            FROM user_data WHERE user_id = %s and pdf_category = %s
            """, (user_id, category)) 
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def get_user_questions(self, user_id):
        try:
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s', (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def get_user_questions_by_category(self, user_id, q_topic):
        try:
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and q_topic = %s', (user_id, q_topic))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def insert_user_question(self, user_id, question: dict):
        try:
            self.cursor.execute("""
            INSERT INTO user_question(user_id, q_topic, q_title, qA, qB, qC, qD, qra, qua, qex, qdiff)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, question["q_topic"], question["q_title"],
                  question["qA"], question["qB"], question["qC"], question["qD"], 
                  question["qra"], question["qua"], question["qex"], question["qdiff"])) 
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    def get_user_incorrect_questions(self, user_id): 
        try:
            self.cursor.execute('SELECT * FROM user_question WHERE user_id = %s and qua <> qra', (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        
    def close(self):
        if self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
