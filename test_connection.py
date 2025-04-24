import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Print environment variables for debugging
print("Environment variables:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="password"
    )
    print("Successfully connected to the database!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {str(e)}") 