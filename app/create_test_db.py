import psycopg2
from app.core.config import settings


conn_string = "database='postgres' host='{}' user='{}' password='{}' port='{}'".format(

    host=settings.DB_HOST,
    user=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    port=settings.DB_PORT,
)
connection = psycopg2.connect(conn_string)
connection.autocommit = True
cursor = connection.cursor()

print("Creating test database")
query = f"CREATE database {settings.POSTGRES_DB}-test;"
cursor.execute(query)
print("Test database created successfully")
