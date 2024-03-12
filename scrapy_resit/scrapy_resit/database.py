import psycopg2

#Database connection for storage of the scrape data
class Database:
    def __init__(self):
        self.connection = psycopg2.connect(
            database="your_database_name",
            user="postgres",
            password="password",
            host="127.0.0.1",
            port=5433,
            host="localhost"
        )
        self.cursor = self.connection.cursor()

    def insert_product(self, item):
        insert_query = """
        INSERT INTO products (title, price, description, details, review_amount, review_rating) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(insert_query, (
            item['product_title'],
            item['product_full-price'],
            item['product_description-text'],
            item['product_specifics_list'],
            item['review_amount'],
            item['review_rating']
        ))
        self.connection.commit()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()