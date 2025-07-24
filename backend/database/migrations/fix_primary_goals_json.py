import sqlite3
import os
import json

# Use the correct path to the database file in backend/
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ai_agent_platform.db'))

print(f"[DEBUG] Using database: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    print("Fixing primary_goals field in scenario_personas table (aggressive double-decode and split)...")
    cursor.execute("SELECT id, primary_goals FROM scenario_personas;")
    rows = cursor.fetchall()
    updated = 0
    for persona_id, primary_goals in rows:
        if primary_goals is None:
            continue
        val = primary_goals
        # Try to decode JSON up to 2 times
        for _ in range(2):
            if isinstance(val, str):
                try:
                    val = json.loads(val)
                except Exception:
                    break
        # If it's a list, skip
        if isinstance(val, list):
            continue
        # If it's a string, split into list and update
        if isinstance(val, str):
            items = [item.strip('• ').strip() for item in val.replace('\r','').split('\n') if item.strip()]
            items = [item for item in items if item]
            json_val = json.dumps(items)
            cursor.execute("UPDATE scenario_personas SET primary_goals = ? WHERE id = ?", (json_val, persona_id))
            updated += 1
    conn.commit()
    print(f"[SUCCESS] Updated {updated} rows in scenario_personas.")
except Exception as e:
    print(f"[ERROR] {e}")
    conn.rollback()
finally:
    conn.close() 