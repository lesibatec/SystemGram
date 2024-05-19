# Your main script
from InstaFunctions import perform_engagement_actions
import os

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))

# Directory containing videos (relative path)
credentials = os.path.join(current_file_directory, "credentials.txt")

# Read usernames and passwords from file
with open(credentials, "r") as file:
    lines = file.readlines()

# Set up other parameters for engagement
usernames_file = "usernames.txt"
message_file = "message.txt"
index_file = "last_processed_index.txt"

# Iterate over lines in the file
for line in lines:
    # Split each line into username and password
    username, password = line.strip().split(",")
    
    # Print username being processed
    print(f"Performing engagement actions for {username}")

    # Call the perform_engagement_actions function
    perform_engagement_actions(username, password, usernames_file, message_file, index_file)
