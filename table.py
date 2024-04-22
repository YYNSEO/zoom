import mysql.connector

def connect_to_database():
    conn = None
    try:
        conn = mysql.connector.connect(
            host="192.168.31.87",
            user="zoom",
            password="0000",
            database="zoom_db"
        )
        if conn.is_connected():
            print("성공")

            cursor = conn.cursor()

            # 테이블 생성 쿼리
            create_table_query = """
            CREATE TABLE IF NOT EXISTS new (
                id  VARCHAR(20) PRIMARY KEY,
                pw  VARCHAR(20)
            )
            """
            cursor.execute(create_table_query)


            cursor.close()
        else:
            print("실패")
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()
            print("Database connection closed")

connect_to_database()
