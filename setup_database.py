import sqlite3

conn = sqlite3.connect("campus_eats.db")
c = conn.cursor()

try:
    # Check whether the restaurant table can be read.
    try:
        c.execute("SELECT restaurant_id, name FROM restaurants")
        c.fetchall()
    except sqlite3.OperationalError:
        c.execute("""
            CREATE TABLE restaurants
            (restaurant_id INTEGER PRIMARY KEY,
             name TEXT)
        """)

    # Check whether the review table can be read.
    try:
        c.execute("""
            SELECT review_id, student_id, restaurant_id,
                   review_taste, serving_speed, value_for_money,
                   freshness, environment, comments, photo
            FROM student_reviews
        """)
        c.fetchall()
    except sqlite3.OperationalError:
        c.execute("""
            CREATE TABLE student_reviews
            (review_id INTEGER PRIMARY KEY,
             student_id INTEGER,
             restaurant_id INTEGER,
             review_taste INTEGER,
             serving_speed INTEGER,
             value_for_money INTEGER,
             freshness INTEGER,
             environment INTEGER,
             comments TEXT,
             photo TEXT)
        """)

    # Add each starter restaurant only if its ID is missing.
    c.execute(
        "SELECT restaurant_id FROM restaurants WHERE restaurant_id = ?",
        (1,)
    )
    if not c.fetchall():
        c.execute(
            "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
            (1, "Subway")
        )

    c.execute(
        "SELECT restaurant_id FROM restaurants WHERE restaurant_id = ?",
        (2,)
    )
    if not c.fetchall():
        c.execute(
            "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
            (2, "Tim Hortons")
        )

    c.execute(
        "SELECT restaurant_id FROM restaurants WHERE restaurant_id = ?",
        (3,)
    )
    if not c.fetchall():
        c.execute(
            "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
            (3, "Harvey")
        )

    conn.commit()

    c.execute("SELECT * FROM restaurants")
    print(c.fetchall())

    c.execute("SELECT * FROM student_reviews")
    print(c.fetchall())
finally:
    conn.close()