import sqlite3
import os

# Use the correct path to the database file in backend/
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_platform.db'))

print(f"[DEBUG] Using database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    print("Adding total_simulations column to users table if missing...")
    cursor.execute("PRAGMA table_info(users);")
    columns = [row[1] for row in cursor.fetchall()]
    if 'total_simulations' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN total_simulations INTEGER DEFAULT 0;")
        print("✓ total_simulations column added.")
    else:
        print("⚠ total_simulations column already exists.")
    conn.commit()
    print("[SUCCESS] Migration complete.")
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close() 