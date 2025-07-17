import pandas as pd
import sqlite3

# Database and CSV file path
csv_file = 'flipkart_product_data.csv'
db_file = 'db.sqlite'

# Connect to (or create) SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the product table (if it doesn't exist)
# Define columns to match your CSV file columns
create_table_query = """
CREATE TABLE IF NOT EXISTS product (
    product_link TEXT PRIMARY KEY,
    title TEXT,
    brand TEXT,
    price INTEGER,
    discount FLOAT,
    avg_rating FLOAT,
    total_ratings INTEGER
);
"""
cursor.execute(create_table_query)

# Commit the table creation
conn.commit()

# Insert DataFrame into the SQLite table
df = pd.read_csv(csv_file)
df.to_sql('product', conn, if_exists='append', index=False)

print("Data inserted into SQLite table successfully.")

# Verify - Read back from the database
result = pd.read_sql_query("SELECT * FROM product LIMIT 5;", conn)
print("Sample from database:")
print(result)

# Close the connection
conn.close()
print("Database connection closed.")
