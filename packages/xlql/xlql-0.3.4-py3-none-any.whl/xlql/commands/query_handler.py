import os
import uuid
import duckdb as dd
import questionary
from tabulate import tabulate
from xlql.core.utils import read_query_from_file, register_csv, get_base_db_location, validate_sql_syntax

def list_databases():
    base_path = get_base_db_location()
    if not base_path:
        print("\033[2m\033[32mTry running `xlql createdb` to get started.\033[0m")
        return
    db_root = os.path.join(base_path, "databases")
    if not os.path.exists(db_root):
        return []
    return [folder for folder in os.listdir(db_root) if os.path.exists(os.path.join(db_root, folder))]

def main(args=None):
    try:
        db_list = list_databases()
        if not db_list:
            print("[ERROR] No databases found. Please create one first.")
            return

        db_name = questionary.select(
            "Select a database:",
            choices=db_list
        ).ask()
        if not db_name:
            print("[INFO] Operation cancelled.")
            return

        # asking for query file path
        query_path = questionary.path(
            "Enter the path to your SQL query file:"
        ).ask()
        if not query_path or not os.path.exists(query_path):
            print(f"[ERROR] Query file '{query_path}' not found.")
            return

        #connecting to DuckDB & register CSVs
        conn = dd.connect(database=':memory:')
        register_csv(conn, db_name)
# reading SQL query
        query = read_query_from_file(query_path).strip()
        query = query.rstrip(';').strip()

        # TODO: Add in a query validator to check the syntax and to check if only the query is read
        
        is_query_valid = validate_sql_syntax(query, conn)

        if not query:
            print("[ERROR] Query file is empty.")
            return
        if is_query_valid == False:
            print("[ERROR] Syntax error in query.")
            return
        
        # asking user if they want to export
        export_choice = questionary.confirm(
            "Do you want to export the results to a file?"
        ).ask()
        
        if export_choice:
            # choosing export format
            export_format = questionary.select(
                "Select export format:",
                choices=["csv", "json", "parquet"]
            ).ask()

            # asking export path
            export_path = questionary.path(
                "Enter the directory path where the file should be saved:"
            ).ask()

            if not os.path.isdir(export_path):
                os.makedirs(export_path, exist_ok=True)

            file_ext = export_format.lower()
            file_name = f"xlql_export_{uuid.uuid4().hex[:8]}.{file_ext}"
            full_export_path = os.path.join(export_path, file_name)

            conn.execute(f"""
                COPY ({query})
                TO '{full_export_path}'
                (FORMAT {export_format.upper()});
            """)

            print(f"[SUCCESS] Query results exported to '{full_export_path}' in {export_format.upper()} format.")
        else:
            # shhowing results in terminal
            result = conn.execute(query).fetchdf()
            if result is not None and not result.empty:
                print(tabulate(result, headers=result.columns, tablefmt="fancy_grid", showindex=False))
            else:
                print("[INFO] Query executed successfully, but returned no results.")

    except Exception as e:
        print(f"[ERROR] {e}")