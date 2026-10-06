import os
import psycopg2
from urllib.parse import urlparse


def get_db_config() -> dict:
    """
    Centralized PostgreSQL connection configuration parser.
    
    Priority order:
    1. DATABASE_URL (if set e.g., postgresql://user:password@host:port/dbname)
    2. Standard uppercase Postgres / Railway env vars (PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD)
    3. Alternative Railway / Docker uppercase env vars (POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD)
    4. Existing lower-case env vars (host, port, database, user, password)
    5. Local development defaults (localhost, 5432, project_sql_agent, postgres, "")
    """
    db_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if db_url:
        try:
            parsed = urlparse(db_url)
            return {
                "host": parsed.hostname or "localhost",
                "port": parsed.port or 5432,
                "dbname": parsed.path.lstrip("/") or "project_sql_agent",
                "user": parsed.username or "postgres",
                "password": parsed.password or "",
            }
        except Exception:
            pass

    host = (
        os.getenv("PGHOST")
        or os.getenv("POSTGRES_HOST")
        or os.getenv("host")
        or "localhost"
    )
    port = int(
        os.getenv("PGPORT")
        or os.getenv("POSTGRES_PORT")
        or os.getenv("port")
        or 5432
    )
    dbname = (
        os.getenv("PGDATABASE")
        or os.getenv("POSTGRES_DB")
        or os.getenv("database")
        or os.getenv("dbname")
        or "project_sql_agent"
    )
    user = (
        os.getenv("PGUSER")
        or os.getenv("POSTGRES_USER")
        or os.getenv("user")
        or "postgres"
    )
    password = (
        os.getenv("PGPASSWORD")
        or os.getenv("POSTGRES_PASSWORD")
        or os.getenv("password")
        or ""
    )

    return {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }


def get_db_connection():
    """Returns a new psycopg2 connection using centralized DB configuration."""
    cfg = get_db_config()
    return psycopg2.connect(**cfg)


class DatabaseUtil:

    def __init__(self, db_config=None):
        self.db_config = db_config or get_db_config()

        try: 
            self.connection = psycopg2.connect(**self.db_config) 
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            self.connection = None

    def schema_details(self, schema_name, target_table=None):

        schema_info_context = ""
        
        if not self.connection:
            return "Error: Database connection is not established."
        connection = self.connection
        cursor = connection.cursor()

        schema_info_context = f"Database Schema: {schema_name}\n"

        try: 
            if target_table:
                cursor.execute("SELECT table_name from information_schema.tables where table_schema = %s AND table_name = %s;", (schema_name, target_table))
            else:
                cursor.execute("SELECT table_name from information_schema.tables where table_schema = %s;", (schema_name,))
            tables_list = cursor.fetchall()

            for table in tables_list:
                table_name = table[0]
                schema_info_context = f"{schema_info_context}\nTable: {table_name}\n"

                # Adding Columns & Data Types
                cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s AND table_schema = %s;", (table_name, schema_name))
                columns_list = cursor.fetchall()

                for column in columns_list:
                    column_name = column[0]
                    data_type = column[1]
                    schema_info_context = f"{schema_info_context}  Column: {column_name}, Data Type: {data_type}\n"

                # Adding Sample Data
                cursor.execute(f"SELECT * FROM {schema_name}.\"{table_name}\" LIMIT 5;")
                sample_data = cursor.fetchall()
                schema_info_context = f"{schema_info_context}  Sample Data:\n"
                for row in sample_data:
                    schema_info_context = f"{schema_info_context}    {row}\n"

        except Exception as e:
            print(f"Error fetching schema details: {e}")
            schema_info_context = f"Error fetching schema details: {e}"

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return schema_info_context

    def execute_sql(self, query):
        try:
            connection = self.connection
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return str(result)
        except Exception as e:
            print(f"Error executing query: {e}")
            return f"Error executing query: {e}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


if __name__ == "__main__":
    obj = DatabaseUtil()
    result = obj.schema_details("public")

    with open("test_schema_details.txt", "w") as f:
        f.write(result)