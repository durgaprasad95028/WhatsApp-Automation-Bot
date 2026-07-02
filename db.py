import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "rishi2006",
    "database": "whatsapp_bot"
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ===== INSERT MESSAGE =====
def insert_message(phone, message, image_path, hour, minute):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages 
        (phone, message, image_path, send_hour, send_minute, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (phone, message, image_path, hour, minute, "pending"))

    conn.commit()
    cursor.close()
    conn.close()


# ===== GET DUE MESSAGES (FIXED LOGIC) =====
def get_due_pending_messages(hour, minute):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, phone, message, image_path
        FROM messages
        WHERE status = 'pending'
        AND send_hour = %s
        AND send_minute BETWEEN %s AND %s
    """, (hour, minute - 1, minute + 1))

    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return data


# ===== MARK AS PROCESSING (IMPORTANT FIX) =====
def mark_as_processing(msg_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages
        SET status = 'processing'
        WHERE id = %s
    """, (msg_id,))

    conn.commit()
    cursor.close()
    conn.close()


# ===== MARK AS SENT =====
def mark_as_sent(msg_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages
        SET status = 'sent',
        error_message = NULL
        WHERE id = %s
    """, (msg_id,))

    conn.commit()
    cursor.close()
    conn.close()


# ===== MARK AS FAILED =====
def mark_as_failed(msg_id, error):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE messages
        SET status = 'failed',
        error_message = %s
        WHERE id = %s
    """, (str(error), msg_id))

    conn.commit()
    cursor.close()
    conn.close()