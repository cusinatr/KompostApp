import sqlite3
from config import DB_NAME
from config import DB_PATH

# ---------------------------------------------------
# Create database and tables
# ---------------------------------------------------


def initialize_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # Volunteers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)
    # Availabilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS availabilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            volunteer TEXT,
            date TEXT,
            availability TEXT
        )
        """)

    conn.commit()
    conn.close()


# ---------------------------------------------------
# Save volunteer submission
# ---------------------------------------------------


def save_availability_submission(volunteer, table_data):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # Ensure volunteer exists
    cursor.execute(
        """
        INSERT OR IGNORE INTO volunteers (name)
        VALUES (?)
        """,
        (volunteer,),
    )

    # Remove previous submission
    cursor.execute(
        """
        DELETE FROM availabilities
        WHERE volunteer = ?
        """,
        (volunteer,),
    )
    # Insert latest submission
    for row in table_data:

        cursor.execute(
            """
            INSERT INTO availabilities (
                volunteer,
                date,
                availability
            )
            VALUES (?, ?, ?)
            """,
            (volunteer, row["date"], row["availability"]),
        )

    conn.commit()
    conn.close()


# ---------------------------------------------------
# Load all availabilities
# ---------------------------------------------------


def load_all_availabilities():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT volunteer, date, availability
        FROM availabilities
        ORDER BY date, volunteer
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------
# Load volunteer availability
# ---------------------------------------------------


def load_volunteer_availability(volunteer):

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT date, availability
        FROM availabilities
        WHERE volunteer = ?
        ORDER BY date
        """,
        (volunteer,),
    )

    rows = cursor.fetchall()

    conn.close()

    return [{"date": row[0], "availability": row[1]} for row in rows]


# ---------------------------------------------------
# Load volunteer statistics
# ---------------------------------------------------


def load_availability_statistics():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            volunteer,
            availability,
            COUNT(*)
        FROM availabilities
        GROUP BY volunteer, availability
        """)

    rows = cursor.fetchall()

    conn.close()

    return rows


# ---------------------------------------------------
# Volunteers who submitted availability
# ---------------------------------------------------


def load_submitted_volunteers():

    conn = sqlite3.connect(DB_NAME)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT volunteer
        FROM availabilities
        """)

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]
