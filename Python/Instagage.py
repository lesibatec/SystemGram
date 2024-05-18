# Your main script
from InstaFunctions import perform_engagement_actions

# Read usernames and passwords from file
with open("credentials.txt", "r") as file:
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
