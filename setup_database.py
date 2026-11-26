import sqlite3

conn = sqlite3.connect("campus_eats.db")
c = conn.cursor()

c.execute("""
    CREATE TABLE restaurants
    (restaurant_id INTEGER PRIMARY KEY,
     name TEXT)
""")

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

c.execute(
    "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
    (1, "Subway")
)

c.execute(
    "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
    (2, "Tim Hortons")
)

c.execute(
    "INSERT INTO restaurants (restaurant_id, name) VALUES (?, ?)",
    (3, "Harvey's")
)

conn.commit()

c.execute("SELECT * FROM restaurants")
print(c.fetchall())

c.execute("SELECT * FROM student_reviews")
print(c.fetchall())

conn.close()