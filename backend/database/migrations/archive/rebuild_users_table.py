import sqlite3
import os

# Use the correct path to the database file in backend/
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_platform.db'))

print(f"[DEBUG] Using database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # 1. Backup users table
    print("Backing up users table to users_backup...")
    cursor.execute("DROP TABLE IF EXISTS users_backup;")
    cursor.execute("CREATE TABLE users_backup AS SELECT * FROM users;")
    print("✓ users_backup created.")

    # 2. Drop the old users table
    print("Dropping old users table...")
    cursor.execute("DROP TABLE users;")
    print("✓ users table dropped.")

    # 3. Create new users table with correct schema
    print("Creating new users table with published_scenarios column...")
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR,
            full_name VARCHAR,
            username VARCHAR,
            password_hash VARCHAR,
            bio TEXT,
            avatar_url VARCHAR,
            role VARCHAR,
            public_agents_count INTEGER,
            public_tools_count INTEGER,
            total_downloads INTEGER,
            reputation_score FLOAT,
            profile_public BOOLEAN,
            allow_contact BOOLEAN,
            is_active BOOLEAN,
            is_verified BOOLEAN,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            published_scenarios INTEGER DEFAULT 0
        );
    ''')
    print("✓ users table created.")

    # 4. Copy data from backup, set published_scenarios to 0
    print("Restoring data from users_backup...")
    cursor.execute('''
        INSERT INTO users (
            id, email, full_name, username, password_hash, bio, avatar_url, role,
            public_agents_count, public_tools_count, total_downloads, reputation_score,
            profile_public, allow_contact, is_active, is_verified, created_at, updated_at, published_scenarios
        )
        SELECT 
            id, email, full_name, username, password_hash, bio, avatar_url, role,
            public_agents_count, public_tools_count, total_downloads, reputation_score,
            profile_public, allow_contact, is_active, is_verified, created_at, updated_at, 0
        FROM users_backup;
    ''')
    print("✓ Data restored to new users table.")

    # 5. Drop backup table
    print("Dropping users_backup table...")
    cursor.execute("DROP TABLE users_backup;")
    print("✓ users_backup table dropped.")

    conn.commit()
    print("[SUCCESS] users table rebuilt with published_scenarios column.")
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close() 