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

print('Creating database')
cursor.execute(
    "select exists(select * from information_schema.tables where table_name=%s)", ('alembic_version',))  # noqa
if not cursor.fetchone()[0]:
    query = "CREATE ROLE {} WITH SUPERUSER CREATEDB CREATEROLE LOGIN ENCRYPTED PASSWORD '{}';".format(  # noqa
        settings.POSTGRES_USER, settings.POSTGRES_PASSWORD
    )
    cursor.execute(query)

    query = f'CREATE database {settings.DB_NAME};'
    cursor.execute(query)
print('Database created successfully')
