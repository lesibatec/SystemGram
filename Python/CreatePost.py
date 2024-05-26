import pyodbc
import random

def get_database_connection(server, database):
    """Create a database connection to SQL Server using Windows authentication."""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
    )
    conn = pyodbc.connect(connection_string)
    return conn

def get_accounts(conn):
    """Fetch account IDs from the database, excluding specific IDs."""
    cursor = conn.cursor()
    # Fetch account IDs excluding IDs 1, 2, 3, and 13
    cursor.execute("SELECT ID FROM Accounts WHERE Status != 'Suspended' AND ID NOT IN (1, 2, 3, 13)")
    account_ids = cursor.fetchall()
    return [account_id[0] for account_id in account_ids]

def get_content(conn):
    """Fetch content from the database."""
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Name, Caption FROM Content")
    content = cursor.fetchall()
    return content

def get_posted_content(conn, account_id):
    """Fetch content IDs already posted by the given account."""
    cursor = conn.cursor()
    cursor.execute("SELECT Content FROM Posts WHERE Account = ?", account_id)
    posted_content = cursor.fetchall()
    return [content_id[0] for content_id in posted_content]

def create_posts(conn):
    """Create entries in the Posts table for each account."""
    cursor = conn.cursor()
    account_ids = get_accounts(conn)
    content = get_content(conn)
    content_ids = [c[0] for c in content]
    
    for account_id in account_ids:
        posted_content_ids = get_posted_content(conn, account_id)
        available_content = [c for c in content if c[0] not in posted_content_ids]
        
        if not available_content:
            print(f"No new content available for account {account_id}.")
            continue
        
        content_entry = random.choice(available_content)
        content_id = content_entry[0]
        name = content_entry[1]
        caption = content_entry[2]
        
        # Insert the post
        cursor.execute(
            "INSERT INTO Posts (WOID, Account, Content, DatePosted, Status) VALUES (?, ?, ?, GETDATE(), 'Pending')",
            (name, account_id, content_id)
        )
        
        conn.commit()

def main():
    # Database connection parameters
    server = 'LAPTOP-0TTTIGAI'
    database = 'GramDB'

    # Establish database connection
    conn = get_database_connection(server, database)

    # Create entries in the Posts table
    create_posts(conn)

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
