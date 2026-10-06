import os
import re
import uuid
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

class DatasetManager:
    def __init__(self):
        self.db_name = os.getenv("database", os.getenv("dbname", "project_sql_agent"))
        self.user = os.getenv("user", "postgres")
        self.password = os.getenv("password", "")
        self.host = os.getenv("host", "localhost")
        self.port = os.getenv("port", "5432")

    def _get_connection(self):
        return psycopg2.connect(
            dbname=self.db_name,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        )

    def sanitize_column_name(self, col_name: str) -> str:
        """Sanitizes raw column names into safe PostgreSQL identifiers."""
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', str(col_name).strip().lower())
        clean = re.sub(r'_+', '_', clean).strip('_')
        if not clean or clean[0].isdigit():
            clean = f"col_{clean}"
        return clean

    def sanitize_table_name(self, filename: str) -> str:
        """Generates a unique PostgreSQL table name for uploaded dataset."""
        base = os.path.splitext(os.path.basename(filename))[0]
        clean_base = re.sub(r'[^a-zA-Z0-9_]', '_', base.strip().lower())
        clean_base = re.sub(r'_+', '_', clean_base).strip('_')
        short_id = uuid.uuid4().hex[:6]
        return f"uploaded_{clean_base}_{short_id}"

    def _map_dtype_to_pg(self, dtype) -> str:
        s = str(dtype)
        if 'int' in s:
            return 'BIGINT'
        elif 'float' in s:
            return 'DOUBLE PRECISION'
        elif 'bool' in s:
            return 'BOOLEAN'
        elif 'datetime' in s:
            return 'TIMESTAMP'
        return 'TEXT'

    def process_and_upload_csv(self, file_object, filename: str):
        """
        Validates CSV, cleans headers, maps types, and creates PostgreSQL table using direct psycopg2.
        """
        try:
            # 1. Read CSV with encoding fallback
            try:
                df = pd.read_csv(file_object)
            except UnicodeDecodeError:
                file_object.seek(0)
                df = pd.read_csv(file_object, encoding="latin1")

            if df.empty:
                return False, "Uploaded CSV file is empty.", None

            # 2. Handle & Sanitize Column Headers
            raw_columns = list(df.columns)
            sanitized_columns = []
            seen = set()

            for col in raw_columns:
                clean_col = self.sanitize_column_name(col)
                final_col = clean_col
                counter = 2
                while final_col in seen:
                    final_col = f"{clean_col}_{counter}"
                    counter += 1
                seen.add(final_col)
                sanitized_columns.append(final_col)

            column_mapping = dict(zip(raw_columns, sanitized_columns))
            df.columns = sanitized_columns

            # 3. Clean date/datetime types if possible
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        parsed_dates = pd.to_datetime(df[col], errors='ignore')
                        if pd.api.types.is_datetime64_any_dtype(parsed_dates):
                            df[col] = parsed_dates
                    except Exception:
                        pass

            # 4. Create Table & Bulk Load to PostgreSQL via psycopg2 execute_values/copy
            table_name = self.sanitize_table_name(filename)
            conn = self._get_connection()
            cur = conn.cursor()

            col_defs = [f'"{col}" {self._map_dtype_to_pg(df[col].dtype)}' for col in df.columns]
            create_sql = f'CREATE TABLE {table_name} ({", ".join(col_defs)});'
            cur.execute(create_sql)

            # Fast batch insert
            import psycopg2.extras
            tuples = [tuple(x) for x in df.to_numpy()]
            cols_str = ",".join([f'"{col}"' for col in df.columns])
            insert_sql = f'INSERT INTO {table_name} ({cols_str}) VALUES %s'
            psycopg2.extras.execute_values(cur, insert_sql, tuples, page_size=1000)

            conn.commit()
            cur.close()
            conn.close()

            # Metadata info
            schema_info = {
                col: self._map_dtype_to_pg(df[col].dtype) for col in df.columns
            }

            dataset_info = {
                "id": table_name,
                "filename": filename,
                "table_name": table_name,
                "row_count": len(df),
                "col_count": len(df.columns),
                "columns": sanitized_columns,
                "column_mapping": column_mapping,
                "schema": schema_info,
                "preview_df": df.head(10)
            }

            return True, "Dataset successfully loaded to PostgreSQL.", dataset_info

        except Exception as e:
            return False, f"Failed to process CSV: {str(e)}", None

    def drop_dataset_table(self, table_name: str) -> bool:
        """Safely drops an uploaded dataset table from PostgreSQL."""
        if not table_name.startswith("uploaded_"):
            return False
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error dropping table {table_name}: {e}")
            return False

