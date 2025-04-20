import sqlite3
from datetime import datetime

def store_ai_evaluation(application_id, match_percentage):
    try:
        conn = sqlite3.connect('recruitment.db')
        cursor = conn.cursor()

        evaluation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notes = f"Match: {match_percentage}%"

        cursor.execute("""
            INSERT INTO ai_evaluations (application_id, evaluation_date, match_percentage, notes)
            VALUES (?, ?, ?, ?)
        """, (application_id, evaluation_date, match_percentage, notes))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error saving AI evaluation: {e}")
