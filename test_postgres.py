import os

os.environ["PGCLIENTENCODING"] = "WIN1252"

import psycopg2

try:
    conn = psycopg2.connect(
        host="127.0.0.1",
        database="Lab_app_training",
        user="postgres",
        password="postgres123",
        port="5432"
    )


    conn.close()

except Exception as e:
    print(repr(e))