
import sqlite3

class Database:
    def __init__(self, db_name="records.db"):
        self.db_name = db_name
        self.create_table()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    address TEXT,
                    contact TEXT,
                    email TEXT
                )
            """)
            conn.commit()

    def add_record(self, name, age, address, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO records (name, age, address, contact, email) VALUES (?, ?, ?, ?, ?)",
                           (name, age, address, contact, email))
            conn.commit()

    def get_records(self, query=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if query:
                search_query = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM records 
                    WHERE name LIKE ? OR email LIKE ? OR address LIKE ?
                """, (search_query, search_query, search_query))
            else:
                cursor.execute("SELECT * FROM records")
            return cursor.fetchall()

    def get_record_by_id(self, record_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM records WHERE id=?", (record_id,))
            return cursor.fetchone()

    def update_record(self, record_id, name, age, address, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE records
                SET name=?, age=?, address=?, contact=?, email=?
                WHERE id=?
            """, (name, age, address, contact, email, record_id))
            conn.commit()

    def verify_not_exists(self, name, email, exclude_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute("SELECT id FROM records WHERE (name=? OR email=?) AND id != ?", (name, email, exclude_id))
            else:
                cursor.execute("SELECT id FROM records WHERE name=? OR email=?", (name, email))
            return cursor.fetchone() is None

    def delete_record(self, record_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
            conn.commit()
