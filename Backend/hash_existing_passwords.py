import sys
import mysql.connector
from werkzeug.security import generate_password_hash

def main():
    try:
        db = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root@123",
            database="synergai"
        )
        cursor = db.cursor(dictionary=True, buffered=True)
        
        # Alter the password column to be long enough for scrypt hashes
        print("Altering password column length...")
        cursor.execute("ALTER TABLE users MODIFY password VARCHAR(512) NOT NULL;")
        
        cursor.execute("SELECT id, email, password FROM users")
        users = cursor.fetchall()
        
        updated_count = 0
        for u in users:
            pw = u["password"]
            # rudimentary check to skip already hashed passwords
            if not (pw.startswith("scrypt:") or pw.startswith("pbkdf2:")):
                hashed = generate_password_hash(pw)
                update_cursor = db.cursor(buffered=True)
                update_cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, u["id"]))
                update_cursor.close()
                updated_count += 1
                print(f"Hashed password for user {u['email']}")

        db.commit()
        cursor.close()
        db.close()
        print(f"Successfully migrated {updated_count} passwords to secure hashes.")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()
