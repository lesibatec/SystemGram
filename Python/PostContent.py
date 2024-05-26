import os
import pandas as pd
from sqlalchemy import create_engine, text
from InstaFunctions import new_upload_post

def get_database_connection(server, database):
    """Create a database connection using SQLAlchemy."""
    connection_string = f"mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(connection_string)
    return engine

def get_posts(engine):
    """Fetch posts data from the database."""
    query = "SELECT ID, WOID, Account, Content FROM Posts WHERE Status != 'Completed'"
    df = pd.read_sql(query, engine)
    return df

def get_credentials(engine, account_id):
    """Fetch credentials from the accounts table based on the account ID."""
    query = f"SELECT username, password FROM accounts WHERE ID = {account_id}"
    df = pd.read_sql(query, engine)
    if not df.empty:
        return df.iloc[0]['username'], df.iloc[0]['password']
    else:
        raise Exception("No credentials found for the specified account ID.")

def get_video_info(engine, content_id):
    """Fetch video path and caption path from the Content table based on the content ID."""
    query = f"SELECT Path, Caption FROM Content WHERE ID = {content_id}"
    df = pd.read_sql(query, engine)
    if not df.empty:
        return df.iloc[0]['Path'], df.iloc[0]['Caption']
    else:
        raise Exception("No video information found for the specified content ID.")

def read_caption_from_file(file_path):
    """Read the caption from the specified file path."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    else:
        raise Exception(f"Caption file not found: {file_path}")

def update_post_status(engine, post_id, status):
    """Update the status of a post in the Posts table."""
    with engine.connect() as connection:
        query = text("UPDATE Posts SET Status = :status WHERE ID = :post_id")
        result = connection.execute(query, {'status': status, 'post_id': post_id})
        connection.commit()  # Explicitly commit the transaction
        print(f"Update result: {result.rowcount} row(s) affected.")

def main():
    # Database connection parameters
    server = 'LAPTOP-0TTTIGAI'
    database = 'GramDB'

    # Establish database connection
    engine = get_database_connection(server, database)

    # Fetch posts
    posts_df = get_posts(engine)

    for index, post_row in posts_df.iterrows():
        post_id = post_row['ID']
        account_id = post_row['Account']
        content_id = post_row['Content']
        
        try:
            username, password = get_credentials(engine, account_id)
            video_path, caption_file_path = get_video_info(engine, content_id)
            caption_text = read_caption_from_file(caption_file_path)

            # Perform post upload here
            new_upload_post(username, password, video_path, caption_text)  # Assuming the upload function accepts caption

            # Update the post status to 'Completed'
            update_post_status(engine, post_id, 'Completed')

        except Exception as e:
            print(f"Error processing post: {e}")
            # Optionally update the post status to 'Failed'
            update_post_status(engine, post_id, 'Failed')

if __name__ == "__main__":
    main()
