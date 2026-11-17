import pandas as pd
from sqlalchemy import create_engine
import urllib.parse
import time
import os

# 1. Database Credentials (Replace 'YOUR_PASSWORD' with your actual MySQL password)
mysql_user = "root"
mysql_password = urllib.parse.quote_plus("Reddy@9441")  # URL-encodes special characters safely
mysql_host = "localhost"
mysql_db = "instacart_db"

# Create the connection engine
engine = create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3306/{mysql_db}")

# 2. Function for small dimension tables (loads all at once)
def load_small_table(file_name, table_name):
    file_path = f"data/{file_name}"
    if not os.path.exists(file_path):
        print(f"Skipping {file_name} - File not found.")
        return

    print(f"Loading {table_name}...")
    df = pd.read_csv(file_path)
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    print(f"Success: {len(df)} rows loaded into {table_name}.\n")

# 3. Function for massive fact tables (loads in chunks)
def load_large_table(file_name, table_name, chunk_size=100000):
    file_path = f"data/{file_name}"
    if not os.path.exists(file_path):
        print(f"Skipping {file_name} - File not found.")
        return

    print(f"Loading {table_name} in chunks of {chunk_size}...")
    start_time = time.time()
    
    # Create a chunk iterator
    chunk_iterator = pd.read_csv(file_path, chunksize=chunk_size)
    
    for i, chunk in enumerate(chunk_iterator):
        # 'replace' creates the table on the first chunk, 'append' adds to it on subsequent chunks
        if_exists_behavior = 'replace' if i == 0 else 'append'
        chunk.to_sql(table_name, con=engine, if_exists=if_exists_behavior, index=False)
        print(f"   -> Inserted chunk {i+1} ({(i+1)*chunk_size} rows processed)")
        
    elapsed_time = round(time.time() - start_time, 2)
    print(f"Finished loading {table_name} entirely in {elapsed_time} seconds.\n")

if __name__ == "__main__":
    print("Starting Instacart Data Ingestion Pipeline...\n")
    
    # Load Small Tables
    load_small_table("departments.csv", "departments")
    load_small_table("aisles.csv", "aisles")
    load_small_table("products.csv", "products")
    
    # Load Large Tables (Chunking Required)
    # orders.csv is ~3.4 million rows
    load_large_table("orders.csv", "orders", chunk_size=100000)
    
    # order_products__prior.csv is ~32.4 million rows
    load_large_table("order_products__prior.csv", "order_products", chunk_size=100000)
    
    print("Data Ingestion Complete! Check MySQL Workbench to verify your tables.")