import os
import pandas as pd
from instagrapi import Client

# Initialize instagrapi client
cl = Client()

# Load session settings from JSON file
def load_session_settings(username):
    settings_file = f"{username}_settings.json"
    try:
        with open(settings_file, 'r') as file:
            cl.load_settings(settings_file)  # Load session settings
            return True
    except FileNotFoundError:
        return False

# Test session by checking if it's valid
def test_session(username):
    session_data = load_session_settings(username)
    if session_data:
        try:
            cl_user_id = cl.user_info_by_username(username).dict()
            return True
        except Exception as e:
            print(f"Error testing session for {username}: {str(e)}")
    return False

# Function to login and save session settings
def login_and_save(username, password):
    try:
        cl.login(username, password)
        settings_file = f"{username}_settings.json"
        cl.dump_settings(settings_file)
        return True
    except Exception as e:
        print(f"Error logging in for {username}: {str(e)}")
        return False

# Function to upload a post using session settings
def upload_post(video_path, caption, username, password):
    if test_session(username):
        try:
            settings_file = f"{username}_settings.json"
            cl.load_settings(settings_file)
            cl.clip_upload(path=video_path, caption=caption)
            return True, f"Post uploaded successfully for {username}!"
        except Exception as e:
            error_message = str(e)
            if "challenge_required" in error_message:
                print(f"Instagram Challenge required. Attempting to log in again.")
                if login_and_save(username, password):
                    return upload_post(video_path, caption, username, password)
                else:
                    print(f"Failed to log in after challenge for {username}.")
                    return False, f"Failed to log in after challenge for {username}."
            else:
                print(f"Error uploading post for {username}: {error_message}")
                return False, f"Error uploading post for {username}: {error_message}"
    else:
        print(f"Session not valid for {username}, attempting to log in again")
        if login_and_save(username, password):
            return upload_post(video_path, caption, username, password)
        else:
            print(f"Failed to upload post for {username}: Unable to login")
            return False, f"Failed to upload post for {username}: Unable to login"

# Get the directory of the current file
current_file_directory = os.path.dirname(os.path.abspath(__file__))

# Directory containing videos (relative path)
video_directory = os.path.join(current_file_directory, "Posts")

# Read the sheet containing video names, captions, and posted status
posts_file = os.path.join(video_directory, "Posts.txt")

# Full path to the posts file
posts_file = os.path.join(current_file_directory, posts_file)

if os.path.isfile(posts_file):
    # Read the posts from the text file into a DataFrame
    df = pd.read_csv(posts_file)

    # Manually provide credentials
    username = "xposemediaza"
    password = "@The2Great7Ref08"

    # Check if all videos have been posted
    if df['Posted'].all():
        # Reset the 'Posted' column to 0
        df['Posted'] = 0
        # Get the details of the first video to post
        first_video = df.iloc[0]
        video_name = first_video['Name']
        caption = first_video['Caption']
        video_path = os.path.join(video_directory, f"{video_name}.mp4")
        # Upload the post
        success, message = upload_post(video_path, caption, username, password)
        if success:
            print(message)
            # Update the 'Posted' status in the DataFrame
            df.loc[df['Name'] == video_name, 'Posted'] = 1
            # Save the updated DataFrame back to the text file
            df.to_csv(posts_file, index=False)
        else:
            print(message)
    else:
        # Find the first video with a 'Posted' status of 0
        next_video = df[df['Posted'] == 0].head(1)
        # Check if there is a video to post
        if not next_video.empty:
            # Get the details of the next video to post
            video_name = next_video.iloc[0]['Name']
            caption = next_video.iloc[0]['Caption']
            video_path = os.path.join(video_directory, f"{video_name}.mp4")
            # Upload the post
            success, message = upload_post(video_path, caption, username, password)
            if success:
                print(message)
                # Update the 'Posted' status in the DataFrame
                df.loc[df['Name'] == video_name, 'Posted'] = 1
                # Save the updated DataFrame back to the text file
                df.to_csv(posts_file, index=False)
            else:
                print(message)
        else:
            print("No pending videos to post.")
else:
    print("Posts file not found")
