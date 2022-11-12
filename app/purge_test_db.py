import psycopg2
from app.core.config import settings

conn_string = "host='{}' user='{}' password='{}' port='{}'".format(
    settings.DB_HOST,
    settings.POSTGRES_USER,
    settings.POSTGRES_PASSWORD,
    settings.DB_PORT,
)
connection = psycopg2.connect(conn_string)
connection.autocommit = True
cursor = connection.cursor()

print("Droping test database!!!")
query = f"DROP database {settings.POSTGRES_DB}_test;"
cursor.execute(query)
print("Test database dropped!!!")
