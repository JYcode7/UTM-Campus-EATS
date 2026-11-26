import sqlite3

class SQLModel:
    def __init__(self):
        self.conn = sqlite3.connect("campus_eats.db")
        self.c = self.conn.cursor()
    def get_all_restr(self):
        self.c.execute("SELECT * FROM restaurants")
        return self.c.fetchall()

    def get_all_reviews(self):
        self.c.execute("SELECT * FROM student_reviews")
        return self.c.fetchall()


    def get_reviews_by_restr(self, restaurant_id):
        self.c.execute("""
            SELECT * FROM student_reviews
            WHERE restaurant_id = ?
        """, (restaurant_id,))

        return self.c.fetchall()

    
    def get_record(self, review_id, student_id):
        self.c.execute("""
            SELECT * FROM student_reviews
            WHERE review_id = ? AND student_id = ?
        """, (review_id, student_id))

        return self.c.fetchall()

    
    def create_review(
        self, student_id, restaurant_id, review_taste,
        serving_speed, value_for_money, freshness,
        environment, comments, photo):
        for score in (
            review_taste, serving_speed, value_for_money,
            freshness, environment
        ):
            if type(score) != int:
                raise ValueError("Each rating must be an integer.")

            if score < 1 or score > 5:
                raise ValueError("Each rating must be between 1 and 5.")
        
        
        self.c.execute("""
            SELECT restaurant_id FROM restaurants
            WHERE restaurant_id = ?
        """, (restaurant_id,))

        
        if not self.c.fetchall():
            raise ValueError("The selected restaurant does not exist.")
        self.c.execute("""SELECT review_id FROM student_reviews
            WHERE student_id = ? AND restaurant_id = ?
        """, (student_id, restaurant_id))


        if self.c.fetchall():
            raise ValueError("You have already reviewed this restaurant. "
                "Edit your existing review.")


        self.c.execute("""
            INSERT INTO student_reviews
            (student_id, restaurant_id, review_taste,serving_speed, value_for_money, freshness,environment, comments, photo)VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student_id, restaurant_id, review_taste,serving_speed, value_for_money, freshness,environment, comments, photo))

        self.conn.commit()


    def update_review(
        self, review_id, student_id, review_taste,
        serving_speed, value_for_money, freshness,
        environment, comments, photo
    ):
        for score in (
            review_taste, serving_speed, value_for_money,
            freshness, environment
        ):
            if type(score) != int:
                raise ValueError("Each rating must be an integer.")

            if score < 1 or score > 5:
                raise ValueError("Each rating must be between 1 and 5.")

        self.c.execute("""
            UPDATE student_reviews
            SET review_taste = ?,
                serving_speed = ?,
                value_for_money = ?,
                freshness = ?,
                environment = ?,
                comments = ?,
                photo = ?
            WHERE review_id = ? AND student_id = ?
        """, (
            review_taste, serving_speed, value_for_money,
            freshness, environment, comments, photo,
            review_id, student_id
        ))

        self.conn.commit()
        return self.c.rowcount
    
    
    def delete_review(self, review_id, student_id):
        self.c.execute("""
            DELETE FROM student_reviews
            WHERE review_id = ? AND student_id = ?
        """, (review_id, student_id))

        self.conn.commit()
        return self.c.rowcount

    
    def close_database(self):
        self.conn.close()



if __name__ == "__main__":
    database = SQLModel()

    try:
        print(database.get_reviews_by_restr(2))
        print(database.get_reviews_by_restr(1))
    finally:
        database.close_database()