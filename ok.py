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
            CREATE TABLE IF NOT EXISTS user (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255)
            )
            """
            cursor.execute(create_table_query)

            # 데이터 삽입 쿼리
            insert_data_query = """
            INSERT INTO user (name, email) VALUES (%s, %s)
            """
            users = [
                ('Alice', 'alice@example.com'),
                ('Bob', 'bob@example.com'),
                ('Charlie', 'charlie@example.com')
            ]
            cursor.executemany(insert_data_query, users)
            conn.commit()  # 데이터 변경사항 저장

            # 테이블 데이터 조회 쿼리
            cursor.execute("SELECT * FROM user")
            rows = cursor.fetchall()

            for row in rows:
                print(row)

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