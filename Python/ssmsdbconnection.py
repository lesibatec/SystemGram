import pyodbc

# Define the connection parameters
server = 'LAPTOP-0TTTIGAI'
database = 'Evolve Academy'
driver = '{ODBC Driver 17 for SQL Server}'  # Use appropriate driver version
trusted_connection = 'yes'  # Use Windows Authentication

# Create a connection string
conn_str = (
    f'DRIVER={driver};'
    f'SERVER={server};DATABASE={database};'
    f'Trusted_Connection={trusted_connection};'
)

# Connect to the database
try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Example: Execute a query
    cursor.execute("SELECT * FROM [Invoice Status]")
    rows = cursor.fetchall()
    # Define the list of tuples
    data = rows

    # Accessing the first tuple
    first_tuple = data[0]
    print(first_tuple)  # Output: ('A', 'Active')

    # Accessing elements within a tuple
    first_code = first_tuple[0]
    first_status = first_tuple[1]
    print(first_code)    # Output: 'A'
    print(first_status)  # Output: 'Active'


    # Close the connection
    cursor.close()
    conn.close()

except Exception as e:
    print(f"An error occurred: {e}")
