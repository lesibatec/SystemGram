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

# Function to load settings using session settings
def load_login_save(username, password):
    if test_session(username):
        try:
            settings_file = f"{username}_settings.json"
            cl.load_settings(settings_file)
            return True, f"Settings loaded successfully for {username}!"
        except Exception as e:
            error_message = str(e)
            if "challenge_required" in error_message:
                print(f"Instagram Challenge required. Attempting to log in again.")
                if login_and_save(username, password):
                    return load_login_save(username, password)
                else:
                    print(f"Failed to log in after challenge for {username}.")
                    return False, f"Failed to log in after challenge for {username}."
            else:
                print(f"Error loading settings for {username}: {error_message}")
                return False, f"Error loading settings for {username}: {error_message}"
    else:
        print(f"Session not valid for {username}, attempting to log in again")
        if login_and_save(username, password):
            return load_login_save(username, password)
        else:
            print(f"Failed to loading settings for {username}: Unable to login")
            return False, f"Failed to loading settings for {username}: Unable to login"

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

def perform_engagement_actions(username, password, usernames_file, message_file, index_file):
    # Read usernames from the file
    with open(usernames_file, 'r') as file:
        usernames = [line.strip() for line in file]

    # Read the index of the last processed username
    try:
        with open(index_file, 'r') as file:
            last_index = int(file.read())
    except FileNotFoundError:
        last_index = 0

    # Get the username for the current run
    current_username = usernames[last_index]

    # Read the comment and DM message from the file
    with open(message_file, 'r', encoding='utf-8') as file:
        comment = file.readline().strip()
        dm_message = file.readline().strip()

    try:
        # Load settings check
        load_login_save(username, password)
        # Get user info for the current username
        user_info_dict = cl.user_info_by_username_v1(current_username).dict()
        # Get the latest media of the user
        media_data = cl.user_medias(user_info_dict['pk'], 1)
        if media_data:
            media = media_data[0]
            # Extract the media ID
            media_pk = media.id
            print(f"Latest media ID for user {current_username}: {media_pk}")
            # Get the likers of the latest media
            media_likers = cl.media_likers(media_pk)
            if media_likers:
                print(f"Top liker for {current_username}: {media_likers[0].username}")
                # Perform actions for each liker
                for liker in media_likers[:5]:
                    print(f"Liker: {liker.username}")
                    # Like and comment on the liker's recent posts
                    try:
                        user_info_liker = cl.user_info_by_username_v1(liker.username).dict()
                        liker_media_data = cl.user_medias(user_info_liker['pk'], 3)
                        i = 0
                        for liker_media in liker_media_data:
                            cl.media_like(liker_media.id)
                            cl.media_comment(liker_media.id, comment)
                            i = i + 1
                            print(f"Liked and Commented on {liker.username} {i} post(s)")
                        # Direct message the liker
                        target_user_id = user_info_liker['pk']
                        cl.direct_send(dm_message, [target_user_id])
                        # Follow the liker
                        cl.user_follow(target_user_id)
                        print(f"Actions performed for liker {liker.username}")
                    except Exception as e:
                        print(f"Error occurred while processing liker {liker.username}: {e}")
            else:
                print(f"No likers found for {current_username}")
        else:
            print(f"No media found for {current_username}")
    except Exception as e:
        print(f"Error occurred while processing user {current_username}: {e}")

    # Update the index of the last processed username
    next_index = (last_index + 1) % len(usernames)
    with open(index_file, 'w') as file:
        file.write(str(next_index))

