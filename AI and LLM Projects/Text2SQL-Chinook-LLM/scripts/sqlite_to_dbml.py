# scripts/sqlite_to_dbml.py
import sqlite3

def sqlite_to_dbml(db_path, output_file="schema.dbml"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]

    dbml_lines = []

    for table in tables:
        dbml_lines.append(f"Table {table} {{")
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            pk = col[5]
            pk_str = " [pk]" if pk else ""
            dbml_lines.append(f"  {col_name} {col_type}{pk_str}")
        dbml_lines.append("}\n")

        cursor.execute(f"PRAGMA foreign_key_list({table});")
        fkeys = cursor.fetchall()
        for fk in fkeys:
            dbml_lines.append(f"Ref: {table}.{fk[3]} > {fk[2]}.{fk[4]}\n")

    with open(output_file, "w") as f:
        f.write("\n".join(dbml_lines))

    print(f"DBML schema written to {output_file}")
