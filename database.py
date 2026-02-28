
import sqlite3
import datetime
import re
import datetime

class Database:
    def _normalize_name(self, name):
        if not name: return ""
        # Remove middle initials/single letters followed by dot or space
        name = re.sub(r'\s+[A-Z](\.|\s+)', ' ', name, flags=re.IGNORECASE)
        # Remove all punctuation and extra whitespace
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip().upper()
        return name

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
                    student_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    age INTEGER,
                    course TEXT,
                    section TEXT,
                    address TEXT,
                    contact TEXT,
                    email TEXT UNIQUE
                )
            """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_email ON records(email)")
            conn.commit()

    def _generate_student_id(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            year = datetime.datetime.now().year
            prefix = f"STD-{year}-"
            
            # Find the highest number for the current year
            cursor.execute("SELECT student_id FROM records WHERE student_id LIKE ? ORDER BY student_id DESC LIMIT 1", (f"{prefix}%",))
            last_id = cursor.fetchone()
            
            if last_id and last_id[0]:
                try:
                    # Extract numeric part from STD-YYYY-NNNN
                    parts = last_id[0].split("-")
                    last_num = int(parts[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
                
            return f"{prefix}{new_num:04d}"

    def add_record(self, name, age, course, section, address, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            student_id = self._generate_student_id()
            cursor.execute("INSERT INTO records (student_id, name, age, course, section, address, contact, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (student_id, name, age, course, section, address, contact, email))
            conn.commit()

    def get_records(self, query=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if query:
                search_query = f"%{query}%"
                cursor.execute("""
                    SELECT * FROM records 
                    WHERE name LIKE ? OR email LIKE ? OR address LIKE ? OR student_id LIKE ? OR course LIKE ? OR section LIKE ?
                """, (search_query, search_query, search_query, search_query, search_query, search_query))
            else:
                cursor.execute("SELECT * FROM records")
            return cursor.fetchall()

    def get_record_by_id(self, record_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM records WHERE id=?", (record_id,))
            return cursor.fetchone()

    def update_record(self, record_id, student_id, name, age, course, section, address, contact, email):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE records
                SET student_id=?, name=?, age=?, course=?, section=?, address=?, contact=?, email=?
                WHERE id=?
            """, (student_id, name, age, course, section, address, contact, email, record_id))
            conn.commit()

    def verify_not_exists(self, student_id, name, email, exclude_id=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            norm_name = self._normalize_name(name)
            
            # Get all records to check normalized names locally (or use a secondary column)
            # For simplicity and small datasets, we'll check name similarities
            if exclude_id:
                cursor.execute("SELECT id, name, email FROM records WHERE id != ?", (exclude_id,))
            else:
                cursor.execute("SELECT id, name, email FROM records")
            
            rows = cursor.fetchall()
            for row in rows:
                db_id, db_name, db_email = row
                if self._normalize_name(db_name) == norm_name:
                    return False
                if db_email.strip().upper() == email.strip().upper():
                    return False
            
            # Also check student_id if provided
            if student_id:
                if exclude_id:
                    cursor.execute("SELECT id FROM records WHERE UPPER(student_id)=UPPER(?) AND id != ?", (student_id, exclude_id))
                else:
                    cursor.execute("SELECT id FROM records WHERE UPPER(student_id)=UPPER(?)", (student_id,))
                if cursor.fetchone():
                    return False
                    
            return True

    def delete_record(self, record_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
            conn.commit()
