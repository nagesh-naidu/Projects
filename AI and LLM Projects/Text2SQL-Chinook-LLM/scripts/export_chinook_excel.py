
import sqlite3
import pandas as pd

def export_all_tables():
    db_path = "../data/Chinook.db"
    output_file = "../data/Chinook_all_tables.xlsx"

    conn = sqlite3.connect(db_path)
    tables = ["Customer", "Invoice", "InvoiceLine", "Track", "Album",
              "Artist", "Genre", "MediaType", "Playlist", "PlaylistTrack", "Employee"]

    with pd.ExcelWriter(output_file) as writer:
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            df.to_excel(writer, sheet_name=table, index=False)

    conn.close()
    print(f"Export complete: {output_file}")
